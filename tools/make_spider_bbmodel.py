import json, math, os, re, uuid, base64
SAMPLE="/workspace/bedrock-samples-v1.26.40.05-full (1)/resource_pack"
TEX="/workspace/Neo's more mobs/NeosMoreMobs_RP/textures/entity/neosmoremobs/spider.png"
OUT="/workspace/Neo's more mobs/work/qa/frames_models/spider.bbmodel"

class M:
    cos=staticmethod(lambda d: math.cos(math.radians(d)))
    sin=staticmethod(lambda d: math.sin(math.radians(d)))
    abs=staticmethod(abs); sqrt=staticmethod(math.sqrt); floor=staticmethod(math.floor)

def ev(expr,t):
    if isinstance(expr,(int,float)): return float(expr)
    e=str(expr).replace("query.anim_time",repr(t)).replace("q.anim_time",repr(t)).replace("this","0")
    return float(eval(e,{"__builtins__":{}},{"math":M}))

src=open(os.path.join(SAMPLE,"models/entity/spider.geo.json")).read()
src=re.sub(r"//[^\n]*","",src)
geo=json.loads(src)["geometry.spider.v1.8"]
tw,th=geo["texturewidth"],geo["textureheight"]

def box_faces(u,v,sx,sy,sz):
    return {"north":{"uv":[u+sz,v+sz,u+sz+sx,v+sz+sy]},"east":{"uv":[u,v+sz,u+sz,v+sz+sy]},
      "south":{"uv":[u+sz+sx+sz,v+sz,u+2*sz+2*sx,v+sz+sy]},"west":{"uv":[u+sz+sx,v+sz,u+2*sz+sx,v+sz+sy]},
      "up":{"uv":[u+sz,v,u+sz+sx,v+sz]},"down":{"uv":[u+sz+sx,v,u+2*sx+sz,v+sz]}}

elements=[]; groups={}; child_elems={}; child_groups={}; roots=[]
for b in geo["bones"]:
    ids=[]
    for i,c in enumerate(b.get("cubes",[])):
        frm=c["origin"]; to=[frm[j]+c["size"][j] for j in range(3)]
        sx,sy,sz=[to[j]-frm[j] for j in range(3)]
        faces=box_faces(c["uv"][0],c["uv"][1],sx,sy,sz)
        for f in faces.values(): f["texture"]=0
        e={"name":f"{b['name']}_{i}","from":frm,"to":to,"origin":b.get("pivot",[0,0,0]),"uv_offset":c["uv"],"faces":faces,"type":"cube","uuid":str(uuid.uuid4())}
        elements.append(e); ids.append(e["uuid"])
    groups[b["name"]]={"name":b["name"],"origin":b.get("pivot",[0,0,0]),"uuid":str(uuid.uuid4())}
    child_elems[b["name"]]=ids
for b in geo["bones"]:
    p=b.get("parent")
    if p and p in groups: child_groups.setdefault(p,[]).append(b["name"])
    else: roots.append(b["name"])
def node(n): return {"uuid":groups[n]["uuid"],"children":[node(c) for c in child_groups.get(n,[])]+child_elems.get(n,[])}
outliner=[node(r) for r in roots]

src=open(os.path.join(SAMPLE,"animations/spider.animation.json")).read()
src=re.sub(r"//[^\n]*","",src); src=re.sub(r"/\*.*?\*/","",src,flags=re.S); src=re.sub(r",\s*([}\]])",r"\1",src)
anims=json.loads(src)["animations"]
base={b:[ev(x,0) for x in ch["rotation"]] for b,ch in anims["animation.spider.default_leg_pose"]["bones"].items()}

def make_clip(name,length,loop,walker=None):
    animators={}
    for bone in base:
        kfs=[]
        for channel in ("rotation",):
            for t in [round(i*length/60,3) for i in range(61)]:
                vals=list(base[bone])
                if walker:
                    w=walker.get(bone)
                    if w:
                        vals=[vals[j]+ev(w[j],t) for j in range(3)]
                kfs.append({"uuid":str(uuid.uuid4()),"channel":channel,"time":t,"interpolation":"linear",
                            "data_points":[{"x":vals[0],"y":vals[1],"z":vals[2]}]})
        animators[groups[bone]["uuid"]]={"name":bone,"type":"bone","keyframes":kfs}
    return {"name":name,"loop":loop,"length":length,"snapping":20,"animators":animators,"uuid":str(uuid.uuid4())}

walkbones={b:ch["rotation"] for b,ch in anims["animation.spider.walk"]["bones"].items()}
bb_anims=[make_clip("walk",10.0,"loop",walkbones), make_clip("idle",2.0,"loop")]
b64=base64.b64encode(open(TEX,"rb").read()).decode()
model={"meta":{"format_version":"4.10","model_format":"bedrock","box_uv":True},"name":"spider",
 "resolution":{"width":tw,"height":th},"elements":elements,"groups":list(groups.values()),"outliner":outliner,
 "textures":[{"path":"","name":"spider.png","folder":"","namespace":"","id":"0","width":tw,"height":th,
 "uv_width":tw,"uv_height":th,"particle":False,"render_mode":"default","visible":True,"internal":True,
 "mode":"bitmap","saved":False,"source":"data:image/png;base64,"+b64,"uuid":str(uuid.uuid4())}],
 "animations":bb_anims}
open(OUT,"w").write(json.dumps(model))
print("wrote",OUT)
