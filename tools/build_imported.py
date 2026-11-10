from pathlib import Path
from PIL import Image
import base64
import json
import math
import shutil
import struct
import sys

sys.path.insert(0, str(Path(__file__).parent))
import build

ROOT = build.ROOT
WORK = build.WORK
MODELS = build.MODELS
TEXTURES = build.TEXTURES
RENDERS = build.RENDERS
RP = build.RP

IDENTITY = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def mat_translation(t):
    m = [row[:] for row in IDENTITY]
    m[0][3], m[1][3], m[2][3] = t
    return m

def mat_scale(s):
    m = [row[:] for row in IDENTITY]
    m[0][0], m[1][1], m[2][2] = s
    return m

def mat_quat(q):
    x, y, z, w = q
    m = [row[:] for row in IDENTITY]
    m[0][0] = 1 - 2 * y * y - 2 * z * z
    m[0][1] = 2 * x * y - 2 * z * w
    m[0][2] = 2 * x * z + 2 * y * w
    m[1][0] = 2 * x * y + 2 * z * w
    m[1][1] = 1 - 2 * x * x - 2 * z * z
    m[1][2] = 2 * y * z - 2 * x * w
    m[2][0] = 2 * x * z - 2 * y * w
    m[2][1] = 2 * y * z + 2 * x * w
    m[2][2] = 1 - 2 * x * x - 2 * y * y
    return m

def node_matrix(node):
    m = mat_translation(node.get("translation", [0, 0, 0]))
    if "rotation" in node:
        m = mat_mul(m, mat_quat(node["rotation"]))
    if "scale" in node:
        m = mat_mul(m, mat_scale(node["scale"]))
    return m

def transform_point(m, p):
    x, y, z = p
    return [
        m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
        m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
        m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3],
    ]

def euler_from_matrix(m):
    sy = max(-1.0, min(1.0, m[0][2]))
    y = math.asin(sy)
    if abs(m[0][2]) < 0.999999:
        x = math.atan2(-m[1][2], m[2][2])
        z = math.atan2(-m[0][1], m[0][0])
    else:
        x = math.atan2(m[2][1], m[1][1])
        z = 0.0
    values = [math.degrees(x), math.degrees(y), math.degrees(z)]
    for i, value in enumerate(values):
        if abs(value) < 0.00001:
            values[i] = 0.0
        values[i] = round(value, 6)
    return values

def accessor(doc, buffer, index):
    a = doc["accessors"][index]
    bv = doc["bufferViews"][a["bufferView"]]
    component = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}[a["componentType"]]
    count = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    offset = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", struct.calcsize(component) * count)
    result = []
    for i in range(a["count"]):
        values = struct.unpack_from("<" + component * count, buffer, offset + i * stride)
        result.append(values[0] if count == 1 else values)
    return result

def face_name(normal):
    axis = max(range(3), key=lambda i: abs(normal[i]))
    positive = normal[axis] >= 0
    if axis == 0:
        return "east" if positive else "west"
    if axis == 1:
        return "up" if positive else "down"
    return "south" if positive else "north"

def load_buffer(doc, gltf_path):
    uri = doc["buffers"][0].get("uri")
    if uri:
        if uri.startswith("data:"):
            return base64.b64decode(uri.split(",", 1)[1])
        return (Path(gltf_path).parent / uri).read_bytes()
    sidecar = Path(gltf_path).with_suffix(".bin")
    return sidecar.read_bytes()

def extract_model(gltf_path, texture_size):
    doc = json.loads(Path(gltf_path).read_text())
    buffer = load_buffer(doc, gltf_path)
    nodes = doc["nodes"]
    world = {}

    def walk(index, parent):
        matrix = mat_mul(parent, node_matrix(nodes[index]))
        world[index] = matrix
        for child in nodes[index].get("children", []):
            walk(child, matrix)

    walk(doc["scenes"][0]["nodes"][0], IDENTITY)

    cubes = []
    for mesh_index, mesh in enumerate(doc["meshes"]):
        primitive = mesh["primitives"][0]
        positions = accessor(doc, buffer, primitive["attributes"]["POSITION"])
        normals = accessor(doc, buffer, primitive["attributes"]["NORMAL"])
        uvs = accessor(doc, buffer, primitive["attributes"]["TEXCOORD_0"])
        accessor_pos = doc["accessors"][primitive["attributes"]["POSITION"]]
        local_min = accessor_pos["min"]
        local_max = accessor_pos["max"]
        local_size = [(local_max[i] - local_min[i]) * 16 for i in range(3)]
        local_size = [max(1.0, value) for value in local_size]
        local_center = [(local_max[i] + local_min[i]) / 2 for i in range(3)]
        node_index = next(i for i, n in enumerate(nodes) if n.get("mesh") == mesh_index)
        matrix = world[node_index]
        center = [v * 16 for v in transform_point(matrix, local_center)]
        rotation = euler_from_matrix(matrix)
        faces = {}
        for normal, uv in zip(normals, uvs):
            key = tuple(round(v, 4) for v in normal)
            faces.setdefault(key, []).append(uv)
        face_data = {}
        for normal_key, coords in faces.items():
            name = face_name(normal_key)
            us = [c[0] * texture_size[0] for c in coords]
            vs = [c[1] * texture_size[1] for c in coords]
            face_data[name] = {
                "uv": [round(min(us), 4), round(min(vs), 4), round(max(us), 4), round(max(vs), 4)]
            }
        if face_data:
            fallback = next(iter(face_data.values()))
            for name in ("north", "east", "south", "west", "up", "down"):
                face_data.setdefault(name, fallback)
        half = [s / 2 for s in local_size]
        cube_from = [round(center[i] - half[i], 6) for i in range(3)]
        cube_to = [round(center[i] + half[i], 6) for i in range(3)]
        cubes.append({
            "mesh": mesh_index,
            "node": node_index,
            "from": cube_from,
            "to": cube_to,
            "origin": [round(v, 6) for v in center],
            "rotation": rotation,
            "faces": face_data,
        })
    return cubes

def extract_hierarchy(gltf_path, texture_size, unit_scale, root_bone=None, synthetic_root=None, rebase_root=False):
    doc = json.loads(Path(gltf_path).read_text())
    buffer = load_buffer(doc, gltf_path)
    nodes = doc["nodes"]
    parent = {}
    for i, node in enumerate(nodes):
        for child in node.get("children", []):
            parent[child] = i
    world = {}

    def walk(index, parent_matrix):
        matrix = mat_mul(parent_matrix, node_matrix(nodes[index]))
        world[index] = matrix
        for child in nodes[index].get("children", []):
            walk(child, matrix)

    if root_bone and rebase_root:
        root_index = next(i for i, n in enumerate(nodes) if n.get("name") == root_bone)
        world[root_index] = IDENTITY
        for child in nodes[root_index].get("children", []):
            walk(child, IDENTITY)
    else:
        for root in doc["scenes"][0]["nodes"]:
            walk(root, IDENTITY)

    subtree = set()
    if root_bone:
        root_index = next(i for i, n in enumerate(nodes) if n.get("name") == root_bone)
        included = set()

        def collect(index):
            subtree.add(index)
            node = nodes[index]
            if node.get("mesh") is None and node.get("children"):
                included.add(index)
            for child in node.get("children", []):
                collect(child)

        collect(root_index)
    else:
        root_index = None
        included = {i for i, n in enumerate(nodes) if n.get("mesh") is None and n.get("children")}

    names = {}
    used = set()
    for index in sorted(included):
        base = nodes[index].get("name") or f"bone_{index}"
        name = base
        if name in used:
            name = f"{base}_{index}"
        used.add(name)
        names[index] = name

    def pivot(index):
        matrix = world[index]
        return [round(matrix[0][3] * unit_scale, 6), round(matrix[1][3] * unit_scale, 6), round(matrix[2][3] * unit_scale, 6)]

    def depth(index):
        value = 0
        current = parent.get(index)
        while current in included:
            value += 1
            current = parent.get(current)
        return value

    groups = []
    if synthetic_root:
        groups.append((synthetic_root, None, [0, 0, 0]))
    for index in sorted(included, key=lambda i: (depth(i), names[i])):
        parent_name = None
        source_parent = parent.get(index)
        if source_parent in included:
            parent_name = names[source_parent]
        elif synthetic_root:
            parent_name = synthetic_root
        groups.append((names[index], parent_name, pivot(index)))

    cubes = []
    for mesh_index, mesh in enumerate(doc["meshes"]):
        primitive = mesh["primitives"][0]
        positions = accessor(doc, buffer, primitive["attributes"]["POSITION"])
        normals = accessor(doc, buffer, primitive["attributes"]["NORMAL"])
        uvs = accessor(doc, buffer, primitive["attributes"]["TEXCOORD_0"])
        accessor_pos = doc["accessors"][primitive["attributes"]["POSITION"]]
        local_min = accessor_pos["min"]
        local_max = accessor_pos["max"]
        local_size = [max(1.0, (local_max[i] - local_min[i]) * unit_scale) for i in range(3)]
        local_center = [(local_max[i] + local_min[i]) / 2 for i in range(3)]
        node_index = next(i for i, n in enumerate(nodes) if n.get("mesh") == mesh_index)
        if root_bone and node_index not in subtree:
            continue
        matrix = world[node_index]
        center = [v * unit_scale for v in transform_point(matrix, local_center)]
        rotation = euler_from_matrix(matrix)
        faces = {}
        for normal, uv in zip(normals, uvs):
            key = tuple(round(v, 4) for v in normal)
            faces.setdefault(key, []).append(uv)
        face_data = {}
        for normal_key, coords in faces.items():
            name = face_name(normal_key)
            us = [c[0] * texture_size[0] for c in coords]
            vs = [c[1] * texture_size[1] for c in coords]
            face_data[name] = {"uv": [round(min(us), 4), round(min(vs), 4), round(max(us), 4), round(max(vs), 4)]}
        if face_data:
            fallback = next(iter(face_data.values()))
            for name in ("north", "east", "south", "west", "up", "down"):
                face_data.setdefault(name, fallback)
        bone_index = parent.get(node_index)
        while bone_index is not None and bone_index not in included:
            bone_index = parent.get(bone_index)
        if bone_index in included:
            bone = names[bone_index]
        else:
            bone = synthetic_root or root_bone or "root"
        half = [value / 2 for value in local_size]
        cubes.append({
            "mesh": mesh_index,
            "name": f"{bone}_{mesh_index}",
            "bone": bone,
            "from": [round(center[i] - half[i], 6) for i in range(3)],
            "to": [round(center[i] + half[i], 6) for i in range(3)],
            "origin": [round(v, 6) for v in center],
            "rotation": rotation,
            "faces": face_data,
        })

    min_y = min(cube["from"][1] for cube in cubes)
    if abs(min_y) > 0.0001:
        shift = -min_y
        for cube in cubes:
            cube["from"][1] += shift
            cube["to"][1] += shift
            cube["origin"][1] += shift
        groups = [(name, parent_name, [origin[0], origin[1] + shift, origin[2]]) for name, parent_name, origin in groups]
    return groups, cubes

BEAR_GROUPS = [
    ("body", None, [0, 13, 0]),
    ("head", "body", [0, 14, -13]),
    ("ear_l", "head", [3.5, 16.5, -16.5]),
    ("ear_r", "head", [-3.5, 16.5, -16.5]),
    ("leg_back_l", "body", [4.5, 10, 6]),
    ("leg_back_r", "body", [-4.5, 10, 6]),
    ("leg_front_l", "body", [3.5, 10, -8]),
    ("leg_front_r", "body", [-3.5, 10, -8]),
    ("tail", "body", [0, 16, 13]),
]
BEAR_MESH_TO_BONE = {
    1: "body", 2: "body", 3: "head", 4: "head",
    5: "ear_l", 6: "ear_r",
    7: "leg_back_l", 8: "leg_back_r", 9: "leg_front_l", 10: "leg_front_r",
}

ELEPHANT_GROUPS = [
    ("body", None, [0, 40, 0]),
    ("head", "body", [0, 34, -13]),
    ("ear_l", "head", [10, 48, -16]),
    ("ear_r", "head", [-10, 48, -16]),
    ("trunk1", "head", [0, 44, -30]),
    ("trunk2", "trunk1", [0, 20, -31]),
    ("leg_back_l", "body", [8.5, 27, 28.5]),
    ("leg_back_r", "body", [-8.5, 27, 28.5]),
    ("leg_front_l", "body", [8.5, 27, -7.5]),
    ("leg_front_r", "body", [-8.5, 27, -7.5]),
    ("tail", "body", [0, 27, 34]),
]
ELEPHANT_MESH_TO_BONE = {
    0: "body", 1: "head", 2: "leg_back_r", 3: "leg_back_l",
    4: "leg_front_l", 5: "leg_front_r", 6: "ear_l", 7: "ear_r",
    8: "trunk1", 9: "trunk2", 10: "head", 11: "head", 12: "head", 13: "head",
    14: "tail",
}

BISON_GROUPS = [
    ("body", None, [0, 28, 0]),
    ("head", "body", [0, 30, -20]),
    ("leg_back_l", "body", [6, 17, 18.5]),
    ("leg_back_r", "body", [-6, 17, 18.5]),
    ("leg_front_l", "body", [7.5, 16, -9.5]),
    ("leg_front_r", "body", [-7.5, 16, -9.5]),
    ("tail", "body", [0, 25, 22]),
]
BISON_MESH_TO_BONE = {
    0: "body", 1: "body",
    2: "leg_back_l", 3: "leg_front_l", 4: "leg_back_r", 5: "leg_front_r",
    6: "head", 7: "head", 8: "head", 9: "head", 10: "head", 11: "head",
    12: "tail", 13: "head",
}

def prepare_texture(mob):
    info = mob["import"]
    source = ROOT / info["texture"]
    target = TEXTURES / f"{mob['id']}.png"
    rp_target = RP / f"{mob['texture']}.png"
    rp_target.parent.mkdir(parents=True, exist_ok=True)
    if info.get("recolor") == "black":
        image = Image.open(source).convert("RGBA")
        pixels = image.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                if lum < 95 and r >= g >= b and r - b > 8:
                    value = max(18, min(52, int(18 + lum * 0.25)))
                    pixels[x, y] = (value, max(8, value - 1), max(6, value - 3), a)
                elif lum < 90:
                    pixels[x, y] = (max(8, int(r * 0.45)), max(8, int(g * 0.42)), max(8, int(b * 0.38)), a)
        image.save(target)
        image.save(rp_target)
    else:
        shutil.copyfile(source, target)
        shutil.copyfile(source, rp_target)
    return Image.open(target).size

def build_model(mob):
    info = mob["import"]
    texture_size = prepare_texture(mob)
    hierarchy = info["rig"] == "hierarchy"
    if info["rig"] == "single":
        cubes = extract_model(ROOT / info["gltf"], texture_size)
        groups = [("body", None, [0, 0, 0])]
        for cube in cubes:
            cube["bone"] = "body"
            cube["name"] = f"body_{cube['mesh']}"
        shift = -min(cube["from"][1] for cube in cubes)
        if shift:
            for cube in cubes:
                cube["from"][1] += shift
                cube["to"][1] += shift
                cube["origin"][1] += shift
        mapping = None
        extra = []
    elif hierarchy:
        cubes = None
        groups, hierarchy_cubes = extract_hierarchy(
            ROOT / info["gltf"],
            texture_size,
            info.get("unit_scale", 16),
            root_bone=info.get("root_bone"),
            synthetic_root=info.get("synthetic_root"),
            rebase_root=info.get("rebase_root", False),
        )
        mapping = None
        extra = []
    elif info["rig"] == "bear":
        cubes = extract_model(ROOT / info["gltf"], texture_size)
        groups = BEAR_GROUPS
        mapping = BEAR_MESH_TO_BONE
        extra = [{
            "name": "tail_cube",
            "bone": "tail",
            "from": [-1.5, 14, 13],
            "to": [1.5, 17, 16],
            "origin": [0, 15.5, 14.5],
            "rotation": [0, 0, 0],
            "faces": {face: {"uv": [8, 0, 12, 4]} for face in ("north", "east", "south", "west", "up", "down")},
        }]
    elif info["rig"] == "bison":
        cubes = extract_model(ROOT / info["gltf"], texture_size)
        groups = BISON_GROUPS
        mapping = BISON_MESH_TO_BONE
        for cube in cubes:
            if cube["mesh"] == 12:
                for axis in (2,):
                    cube["from"][axis] -= 3.0
                    cube["to"][axis] -= 3.0
                    cube["origin"][axis] -= 3.0
        extra = []
    else:
        cubes = extract_model(ROOT / info["gltf"], texture_size)
        groups = ELEPHANT_GROUPS
        mapping = ELEPHANT_MESH_TO_BONE
        extra = []
    model_rel = f"work/models/{mob['id']}.bbmodel"
    model_path = ROOT / model_rel
    if model_path.exists():
        model_path.unlink()
    created = build.run_bb("bbmodel_create", {
        "file": model_rel,
        "format": "bedrock",
        "resolution": {"width": texture_size[0], "height": texture_size[1]},
        "overwrite": True,
    })
    revision = created["revision"]
    operations = [{
        "op": "set_model_properties",
        "name": mob["name"],
        "model_identifier": mob["geometry"],
        "resolution": {"width": texture_size[0], "height": texture_size[1]},
    }]
    for name, parent, origin in groups:
        op = {"op": "add_group", "name": name, "origin": origin}
        if parent:
            op["parent"] = parent
        operations.append(op)
    if hierarchy:
        cubes = hierarchy_cubes
    cube_names = []
    for cube in cubes:
        if "bone" in cube:
            bone = cube["bone"]
            name = cube["name"]
        else:
            bone = mapping.get(cube["mesh"])
            if bone is None:
                continue
            name = f"{bone}_{cube['mesh']}"
        cube_names.append(name)
        operations.append({
            "op": "add_cube",
            "name": name,
            "from": cube["from"],
            "to": cube["to"],
            "origin": cube["origin"],
            "rotation": cube["rotation"],
            "box_uv": False,
            "faces": cube["faces"],
            "parent": bone,
        })
    for cube in extra:
        cube_names.append(cube["name"])
        operations.append({
            "op": "add_cube",
            "name": cube["name"],
            "from": cube["from"],
            "to": cube["to"],
            "origin": cube["origin"],
            "rotation": cube["rotation"],
            "box_uv": False,
            "faces": cube["faces"],
            "parent": cube["bone"],
        })
    edited = build.run_bb("bbmodel_edit", {
        "file": model_rel,
        "expected_revision": revision,
        "operations": operations,
    })
    revision = edited["revision"]
    textured = build.run_bb("bbmodel_add_texture", {
        "file": model_rel,
        "expected_revision": revision,
        "image": f"work/textures/{mob['id']}.png",
        "name": f"{mob['id']}_texture",
        "assign_to": cube_names,
    })
    revision = textured["revision"]
    anim_ops = build.animation_ops(mob)
    for index in range(0, len(anim_ops), 350):
        result = build.run_bb("bbmodel_edit", {
            "file": model_rel,
            "expected_revision": revision,
            "operations": anim_ops[index:index + 350],
        })
        revision = result["revision"]
    validation = build.run_bb("bbmodel_validate", {"file": model_rel})
    (MODELS / f"{mob['id']}.validation.json").write_text(json.dumps(validation, indent=2))
    anim_validation = build.run_bb("bbmodel_validate_animations", {"file": model_rel})
    (MODELS / f"{mob['id']}.animation_validation.json").write_text(json.dumps(anim_validation, indent=2))
    sheet_text = build.run_bb_raw("bbmodel_contact_sheet", {
        "file": model_rel,
        "views": ["front", "right", "back", "left", "three-quarter"],
        "size": 384,
        "orthographic": True,
        "lighting": "flat",
    })
    (MODELS / f"{mob['id']}.sheet.txt").write_text(sheet_text)
    for line in sheet_text.splitlines():
        if ": " not in line:
            continue
        label, image_path = line.split(": ", 1)
        source = Path(image_path)
        if label in ("front", "right", "back", "left", "three-quarter") and source.exists():
            shutil.copyfile(source, RENDERS / f"{mob['id']}_{label}.png")
    for clip, time in {"idle": 1.0, "walk": 0.3, "run": 0.2, "attack": 0.3}.items():
        if clip not in mob["clips"]:
            continue
        out = f"work/renders/{mob['id']}_{clip}.png"
        target = ROOT / out
        if target.exists():
            target.unlink()
        build.run_bb("bbmodel_render", {
            "file": model_rel,
            "view": "three-quarter",
            "width": 512,
            "height": 512,
            "lighting": "outdoor",
            "clip": f"animation.neosmoremobs.{mob['id']}.{clip}",
            "time": time,
            "output": out,
            "overwrite": True,
        })
    out_geo = f"NeosMoreMobs_RP/models/entity/{mob['id']}.geo.json"
    geo_path = ROOT / out_geo
    if geo_path.exists():
        geo_path.unlink()
    build.run_bb("bbmodel_export_bedrock_geometry", {
        "file": model_rel,
        "output": out_geo,
        "identifier": mob["geometry"],
        "visible_bounds": True,
        "overwrite": True,
    })

def main():
    for mob in build.MOBS:
        if "import" in mob:
            print(f"importing {mob['id']}", flush=True)
            build_model(mob)

if __name__ == "__main__":
    main()
