"""Minimal little-endian (Bedrock) NBT reader/writer for .mcstructure files."""
import struct

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


def read_nbt(data):
    pos = 0

    def u8():
        nonlocal pos
        v = data[pos]; pos += 1; return v

    def fmt(fmt_):
        nonlocal pos
        v = struct.unpack_from(fmt_, data, pos)[0]; pos += struct.calcsize(fmt_); return v

    def string():
        nonlocal pos
        n = struct.unpack_from("<H", data, pos)[0]; pos += 2
        s = data[pos:pos + n].decode("utf-8", "replace"); pos += n; return s

    def payload(t):
        nonlocal pos
        if t == TAG_BYTE:
            return u8()
        if t == TAG_SHORT:
            return fmt("<h")
        if t == TAG_INT:
            return fmt("<i")
        if t == TAG_LONG:
            return fmt("<q")
        if t == TAG_FLOAT:
            return fmt("<f")
        if t == TAG_DOUBLE:
            return fmt("<d")
        if t == TAG_BYTE_ARRAY:
            n = fmt("<i"); return list(data[pos:pos + n]) if not _skip(n) else None
        if t == TAG_STRING:
            return string()
        if t == TAG_LIST:
            et = u8(); n = struct.unpack_from("<i", data, pos)[0]; pos += 4
            return [payload(et) for _ in range(n)]
        if t == TAG_COMPOUND:
            out = {}
            while True:
                tt = u8()
                if tt == TAG_END:
                    return out
                name = string()
                out[name] = payload(tt)
        if t == TAG_INT_ARRAY:
            n = fmt("<i"); return [fmt("<i") for _ in range(n)]
        if t == TAG_LONG_ARRAY:
            n = fmt("<i"); return [fmt("<q") for _ in range(n)]
        raise ValueError(f"tag {t}")

    def _skip(n):
        nonlocal pos
        pos += n
        return True

    t = u8()
    name = string() if t != TAG_END else ""
    return {name: payload(t)}


def _tag(t, name, payload_bytes):
    nm = name.encode("utf-8")
    return bytes([t]) + struct.pack("<H", len(nm)) + nm + payload_bytes


def nbt_string(name, value):
    v = value.encode("utf-8")
    return _tag(TAG_STRING, name, struct.pack("<H", len(v)) + v)


def nbt_int(name, value):
    return _tag(TAG_INT, name, struct.pack("<i", value))


def nbt_compound(name, body):
    return _tag(TAG_COMPOUND, name, body + b"\x00")


def nbt_list_int(name, values):
    return _tag(TAG_LIST, name, bytes([TAG_INT]) + struct.pack("<i", len(values)) + b"".join(struct.pack("<i", v) for v in values))


def nbt_list_compound(name, bodies):
    return _tag(TAG_LIST, name, bytes([TAG_COMPOUND]) + struct.pack("<i", len(bodies)) + b"".join(b + b"\x00" for b in bodies))


def nbt_list_list_int(name, lists):
    body = b"".join(bytes([TAG_INT]) + struct.pack("<i", len(l)) + b"".join(struct.pack("<i", v) for v in l) for l in lists)
    return _tag(TAG_LIST, name, bytes([TAG_LIST]) + struct.pack("<i", len(lists)) + body)
