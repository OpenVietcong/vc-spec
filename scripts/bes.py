#!/usr/bin/env python3

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  version 2 as published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
bes.py - util for checking BES files for integrity
"""

import sys
import argparse
import os
import struct
import logging
import math

__author__ = "Jan Havran"

logging.VERBOSE = logging.DEBUG + 5

def hex_dump(data, index):
    for i in range(len(data)):
        if i % 16 == 0:
            sys.stdout.write("{}{:04x}:".format(" "*(index*2), i))
        sys.stdout.write(" {:02x}".format(data[i]))
        if i % 16 == 15:
            print()
    print()

def pchar_to_string(pchar):
    """
    Convert C Windows-1250 string into Python string
    """
    return str(pchar, 'cp1250').strip(chr(0))

def trans_mat(t, r, s):
    """
    Compute transformation matrix 4x4 from
    translation, rotation and scale vectors
    """
    from numpy import matmul, identity, sin, cos

    mt = identity(4)
    mr = identity(4)
    rx = identity(4)
    ry = identity(4)
    rz = identity(4)
    ms = identity(4)
    m = identity(4)

    # translation
    mt[3][0] = t[0]
    mt[3][1] = t[1]
    mt[3][2] = t[2]

    # rotation
    rx[1][2] = sin(r[0])
    rx[2][1] = -rx[1][2]
    rx[1][1] = rx[2][2] = cos(r[0])

    ry[2][0] = sin(r[1])
    ry[0][2] = -ry[2][0]
    ry[0][0] = ry[2][2] = cos(r[1])

    rz[0][1] = sin(r[2])
    rz[1][0] = -rz[0][1]
    rz[0][0] = rz[1][1] = cos(r[2])

    mr = matmul(ry, rx)
    mr = matmul(rz, mr)

    # scale
    ms[0][0] = s[0]
    ms[1][1] = s[1]
    ms[2][2] = s[2]

    m = matmul(mr, mt)
    m = matmul(ms, m)

    return m

class BESMesh(object):
    def __init__(self, vertices, faces, material):
        self.vertices = vertices
        self.faces = faces
        self.material = material

class BESVertex(object):
    class Flags:
        XYZ    = 0x002
        Normal = 0x010

        Tex0   = 0x000
        Tex1   = 0x100
        Tex2   = 0x200
        Tex3   = 0x300
        Tex4   = 0x400
        Tex5   = 0x500
        Tex6   = 0x600
        Tex7   = 0x700
        Tex8   = 0x800

        TexcountMask  = 0xf00
        TexcountShift = 8
        TexcountMax   = 8

    def __init__(self, coords, normals, uv = []):
        self.coords = coords
        self.normals = normals
        self.uv = uv

class BES(object):
    class Header:
        sig = b'BES\x00'
        vers = [b'0100']
        lib_vers = {
            0x00000000 : "AutoSelect",
            0x17700d00 : "3DS Max 6",
            0x1b580f00 : "3DS Max 7",
            0x1f401100 : "3DS Max 8"
        }

    class BlockID:
        Object         = 0x0001
        Model          = 0x0030
        Mesh           = 0x0031
        Vertices       = 0x0032
        Faces          = 0x0033
        Properties     = 0x0034
        Transformation = 0x0035
        Unk36          = 0x0036
        Unk38          = 0x0038
        Info           = 0x0070
        Material       = 0x1000
        Standard       = 0x1001
        PteroMat       = 0x1002

    class BlockPresence:
        OptSingle   = 0  # <0;1>
        OptMultiple = 1  # <0;N>
        ReqSingle   = 2  # <1;1>
        ReqMultiple = 3  # <1;N>

    class Standard:
        maps = ["Diffuse Color", "Displacement", "Bump", "Ambient Color",
            "Specular Color", "Specular Level", "Glossiness", "Self-Illumination",
            "UNKNOWN", "Filter Color", "Reflection", "Refraction"]

    class PteroMat:
        texs = ["Diffuse #1 - Ground", "Diffuse #2 - Multitexture", "Diffuse #3 - Overlay",
            "LightMap", "Environment #1", "UNKNOWN",
            "LightMap (Engine Lights)", "Diffuse #3 - Overlay Multitexture"]
        offset = 16
        transparency = { 0x202D : "- none - (opaque)",
                 0x3023 : "#0 - transparent, zbufwrite, sort",
                 0x3123 : "#1 - transparent, zbufwrite, sort, 1-bit alpha",
                 0x3223 : "#2 - translucent, no_zbufwrite, sort",
                 0x3323 : "#3 - transparent, zbufwrite, nosort, 1-bit alpha",
                 0x3423 : "#4 - translucent, add with background, no_zbufwrite, sort"}

        def parseTexture(data, index, texID):
            (coord, name_size) = BES.unpack("<II", data)
            (name,) = BES.unpack("<" + str(name_size) + "s", data[8:])

            if BES.PteroMat.texs[texID - BES.PteroMat.offset] == "UNKNOWN":
                logging.warning("Undocumented bitmap detected")

            if coord & 0xFFFC:
                logging.warning("Unknown bits in texture ({:08x})".format(coord))

            #Determine the texture type by flag in coord field
            texFlag = coord >> 16
            texPos = 0
            while texFlag >> 1:
                texFlag = texFlag >> 1
                texPos += 1
            sPrint = "\n{}{} texture - ({}): {}".format(
                " "*((index+1)*2), BES.PteroMat.texs[texPos],
                name_size, pchar_to_string(name))

            if coord & 0x1:
                sPrint += ", U tile"
            if coord & 0x2:
                sPrint += ", V tile"

            return (8 + name_size, sPrint)

    def __init__(self, data):
        self.vertices = []
        self.faces = []
        self.data = data
        self.ver = b'0100'

    def unpack(fmt, data):
        st_fmt = fmt
        st_len = struct.calcsize(st_fmt)
        st_unpack = struct.Struct(st_fmt).unpack_from
        return st_unpack(data[:st_len])

    def parse_header(self):
        (sig, bes_ver, lib_ver, unk2) = BES.unpack("<4s4sII", self.data)

        if sig != BES.Header.sig:
            raise RuntimeError("  Invalid header signature")

        if bes_ver not in BES.Header.vers:
            logging.error("  Unsupported BES version: {}".format(bes_ver))
            bes_ver = None
        else:
            logging.log(logging.VERBOSE, "BES version: {}".format(bes_ver))

        if lib_ver not in BES.Header.lib_vers:
            logging.warning("  Unknown exporter version: {:08x}".format(lib_ver))
        else:
            logging.log(logging.VERBOSE, "Exporter version: {}".format(
                BES.Header.lib_vers[lib_ver]))

        self.ver = bes_ver
        return bes_ver

    def parse_preview(self):
        if len(self.data) < 0x3010:
            raise RuntimeError("  Missing model preview image")

        return self.data[0x10:0x3010]

    def parse_data(self):
        res = self.parse_blocks({BES.BlockID.Object  : BES.BlockPresence.ReqSingle,
                    BES.BlockID.Info : BES.BlockPresence.OptSingle},
                    self.data[0x3010:], 0)

    def parse_block_desc(self, data):
        return BES.unpack("<II", data)

    def parse_block_by_label(self, label, subblock, index):
        if   label == BES.BlockID.Object:
            return self.parse_block_object(subblock, index)
        elif label == BES.BlockID.Model:
            return self.parse_block_model(subblock, index)
        elif label == BES.BlockID.Mesh:
            return self.parse_block_mesh(subblock, index)
        elif label == BES.BlockID.Vertices:
            return self.parse_block_vertices(subblock, index)
        elif label == BES.BlockID.Faces:
            return self.parse_block_faces(subblock, index)
        elif label == BES.BlockID.Properties:
            return self.parse_block_properties(subblock, index)
        elif label == BES.BlockID.Transformation:
            return self.parse_block_transformation(subblock, index)
        elif label == BES.BlockID.Unk36:
            return self.parse_block_unk36(subblock, index)
        elif label == BES.BlockID.Unk38:
            return self.parse_block_unk38(subblock, index)
        elif label == BES.BlockID.Info:
            return self.parse_block_info(subblock, index)
        elif label == BES.BlockID.Material:
            return self.parse_block_material(subblock, index)
        elif label == BES.BlockID.Standard:
            return self.parse_block_standard(subblock, index)
        elif label == BES.BlockID.PteroMat:
            return self.parse_block_ptero_mat(subblock, index)
        else:
            logging.warning("Unknown block {}".format(hex(label)))
            hex_dump(subblock, index)

    def parse_blocks(self, blocks, data, index):
        # Init return values
        ret = dict()
        for label in blocks:
            if (blocks[label] == BES.BlockPresence.OptSingle or
            blocks[label] == BES.BlockPresence.ReqSingle):
                ret[label] = None
            else:
                ret[label] = []

        # Search for all blocks
        start = 0
        while len(data[start:]) > 0:
            (label, size) = self.parse_block_desc(data[start:])
            subblock = data[start + 8: start + size]

            if label not in blocks:
                logging.warning("{}Unexpected block {:04X} [{} B] at this location".format(
                    " "*(index*2), label, size))
            else:
                if (blocks[label] == BES.BlockPresence.OptSingle or
                blocks[label] == BES.BlockPresence.ReqSingle):
                    blocks.pop(label)
                    ret[label] = self.parse_block_by_label(label, subblock, index)
                else:
                    ret[label].append(self.parse_block_by_label(label, subblock, index))
            start += size

        if start != len(data):
            logging.error("{}Block {:04X} contains more data than expected".format(
                " "*(index*2), label))

        # Check if all required blocks were found in this block
        for label in blocks:
            if ((blocks[label] == BES.BlockPresence.ReqSingle) or
            (blocks[label] == BES.BlockPresence.ReqMultiple and label not in ret)):
                logging.warning("Invalid number of occurrences of block {:04X}".format(label))

        return ret

    def parse_block_object(self, data, index):
        (children, name_size) = BES.unpack("<II", data)
        (name,) = BES.unpack("<" + str(name_size) + "s", data[8:])
        logging.log(logging.VERBOSE, "{}Object ({} B) - children: {}, name({}): {}".format(
            " "*(index*2), len(data), children, name_size,    pchar_to_string(name)))

        res = self.parse_blocks({BES.BlockID.Object        : BES.BlockPresence.OptMultiple,
                    BES.BlockID.Model          : BES.BlockPresence.OptSingle,
                    BES.BlockID.Properties     : BES.BlockPresence.OptSingle,
                    BES.BlockID.Transformation : BES.BlockPresence.OptSingle,
                    BES.BlockID.Unk38          : BES.BlockPresence.OptSingle,
                    BES.BlockID.Material       : BES.BlockPresence.OptSingle},
                    data[8 + name_size:], index + 1)

        if len(res[BES.BlockID.Object]) != children:
            logging.error("{}Number of object children does not match".format(
                " "*(index*2)))

    def parse_block_model(self, data, index):
        (children,) = BES.unpack("<I", data)
        logging.log(logging.VERBOSE, "{}Model ({} B) - Number of meshes: {:08x}".format(
            " "*(index*2), len(data), children))

        res = self.parse_blocks({BES.BlockID.Mesh          : BES.BlockPresence.OptMultiple,
                    BES.BlockID.Properties     : BES.BlockPresence.ReqSingle,
                    BES.BlockID.Transformation : BES.BlockPresence.ReqSingle,
                    BES.BlockID.Unk36          : BES.BlockPresence.OptSingle},
                    data[4:], index + 1)

        if len(res[BES.BlockID.Mesh]) != children:
            logging.error("{}Number of model children does not match".format(
                " "*(index*2)))

    def parse_block_mesh(self, data, index):
        """ Parse Mesh block and return BESMesh instance """
        (material,) = BES.unpack("<I", data)
        logging.log(logging.VERBOSE, "{}Mesh ({} B) - Material: {:08x}".format(
            " "*(index*2), len(data), material))

        res = self.parse_blocks({BES.BlockID.Vertices : BES.BlockPresence.ReqSingle,
                    BES.BlockID.Faces       : BES.BlockPresence.ReqSingle},
                    data[4:], index + 1)

        vertices = res[BES.BlockID.Vertices]
        faces    = res[BES.BlockID.Faces]

        maxVertexID = max(max(faces, key=lambda item:item[1]))
        if maxVertexID >= len(vertices):
            logging.error("{}Vertex ID ({}) bigger than total number of vertices ({})".format(
                " "*(index*2), maxVertexID, len(vertices)))

        return BESMesh(vertices, faces, material)

    def parse_block_vertices(self, data, index):
        """
        Parse Vertices block and return list of BESVertex instances.
        Each instance is made of  x,y,z coords, normals and uv coords (variable length)
        """
        (count, size, flags) = BES.unpack("<III", data)
        texCnt = (flags & BESVertex.Flags.TexcountMask) >> BESVertex.Flags.TexcountShift
        flagsMin = BESVertex.Flags.XYZ | BESVertex.Flags.Normal
        flagsMax = flagsMin | BESVertex.Flags.TexcountMask
        vertices = []

        logging.log(logging.VERBOSE, "{}Vertices ({} B) - count: {}, size: {}, flags: {:08x}".format(
            " "*(index*2), len(data), count, size, flags))

        if (flags & flagsMin) != flagsMin or (flags | flagsMax) != flagsMax:
            logging.error("{}Unsupported vertex flags: {:08x}".format(
                " "*(index*2), flags))
            return vertices
        if texCnt > BESVertex.Flags.TexcountMax:
            logging.error("{}Texture count over limit: {}".format(
                " "*(index*2), texCnt))
            return vertices
        if 24 + 8 * texCnt != size:
            logging.error("{}Vertex size do not match".format(
                " "*(index*2)))
            return vertices
        elif len(data[12:]) != size * count:
            logging.error("{}Block size do not match".format(
                " "*(index*2)))
            return vertices

        ptr = 12
        for i in range(count):
            coords = BES.unpack("<fff", data[ptr:])
            ptr += 12
            normals = BES.unpack("<fff", data[ptr:])
            ptr += 12

            uv_array = []
            for texID in range(texCnt):
                uv = BES.unpack("<ff", data[ptr:])
                uv_array.append(uv)
                ptr += 8

            vertices.append(BESVertex(coords, normals, uv_array))

        return vertices

    def parse_block_faces(self, data, index):
        """
        Parse Faces block and return list of tuples.
        Each tuple means one face made of 3 integers (vertices IDs)
        """
        (count,) = BES.unpack("<I", data)
        faces = []

        logging.log(logging.VERBOSE, "{}Faces ({} B) - count: {}".format(
            " "*(index*2), len(data), count))

        if len(data[4:]) != count * 12:
            logging.error("{}Block size do not match".format(
                " "*(index*2)))
            return faces

        ptr = 4
        for i in range(count):
            face = BES.unpack("<III", data[ptr:])
            faces.append(face)
            ptr += 12

        return faces

    def parse_block_properties(self, data, index):
        (count, ) = BES.unpack("<I", data)
        (prop,) = BES.unpack("<" + str(count) + "s", data[4:])
        logging.log(logging.VERBOSE, "{}Properties ({} B): {}".format(
            " "*(index*2), len(data), pchar_to_string(prop)))

        if count + 4 != len(data):
            logging.error("{}Block size do not match: {} vs {}".format(
                " "*(index*2), len(data), count + 4))

    def parse_block_transformation(self, data, index):
        """
        Parse Transformation block and return tuple of three tuples and one array.
        Tuples are translation, rotation, scale and contains tranformation values (x, y, z).
        Array is transformation matrix 4x4
        """
        if len(data) != 100:
            logging.error("{}Block size do not match".format(" "*(index*2)))

        t = BES.unpack("<fff", data[00:12]) # translation
        r = BES.unpack("<fff", data[12:24]) # rotation
        s = BES.unpack("<fff", data[24:36]) # scale
        m = []
        m.append(list(BES.unpack("<ffff", data[36:52])))
        m.append(list(BES.unpack("<ffff", data[52:68])))
        m.append(list(BES.unpack("<ffff", data[68:84])))
        m.append(list(BES.unpack("<ffff", data[84:100])))

        mn = trans_mat(t, r, s)

        for i in range(4):
            for j in range(4):
                if not math.isclose(m[i][j], mn[i][j], rel_tol=1e-5, abs_tol=1e-6):
                    logging.info("{}transformation matrix does not match"
                        "(index [{}][{}]\n"
                        "{}  original: {} vs computed: {}".format(
                        " "*(index*2), i, j,
                        " "*(index*2), m[i][j], mn[i][j]))

        sPrint = ("{}Transformation ({} B)\n{}  translation: [{}][{}][{}]\n"
            "{}  rotation: [{}][{}][{}]\n{}  scale: [{}][{}][{}]\n"
            "{}  matrix:\n"
            "{}    [{}][{}][{}][{}]\n"
            "{}    [{}][{}][{}][{}]\n"
            "{}    [{}][{}][{}][{}]\n"
            "{}    [{}][{}][{}][{}]")
        sPrint = sPrint.format(" "*(index*2), len(data),
            " "*(index*2), t[0], t[1], t[2],
            " "*(index*2), r[0], r[1], r[2],
            " "*(index*2), s[0], s[1], s[2],
            " "*(index*2),
            " "*(index*2), m[0][0], m[0][1], m[0][2], m[0][3],
            " "*(index*2), m[1][0], m[1][1], m[1][2], m[1][3],
            " "*(index*2), m[2][0], m[2][1], m[2][2], m[2][3],
            " "*(index*2), m[3][0], m[3][1], m[3][2], m[3][3])
        logging.log(logging.VERBOSE, sPrint),

        return (t, r, s, m)

    def parse_block_unk36(self, data, index):
        (unknown,) = BES.unpack("<I", data)
        logging.log(logging.VERBOSE, "{}Unk36 ({} B - unknown: {:08x})".format(
            " "*(index*2), len(data), unknown))

        if len(data) != 4:
            logging.error("{}Block size do not match".format(" "*(index*2)))

    def parse_block_unk38(self, data, index):
        logging.log(logging.VERBOSE, "{}Unk38 ({} B)".format(
            " "*(index*2), len(data)))

    def parse_block_info(self, data, index):
        """
        Parse Info block and return tuple of:
        author name, comment and number of faces in this BES file
        """
        (author_size, comment_size, faces) = BES.unpack("<III", data)

        if author_size > 64:
            logging.error("{}Invalid author length ({})".format(
                " "*(index*2), name_size))
            return ("", "", faces)
        if len(data) != 76 + comment_size:
            logging.error("{}Block size do not match: {} vs {}".format(
                " "*(index*2), len(data), 76 + comment_size))
            return ("", "", faces)

        author = pchar_to_string(BES.unpack("<" + str(author_size) + "s", data[12:])[0])
        comment = pchar_to_string(BES.unpack("<" + str(comment_size) + "s", data[76:])[0])
        logging.log(logging.VERBOSE,
            "{}Info ({} B) - author({}): {}, comment({}): {}, faces: {}".format(
                " "*(index*2), len(data), author_size, author,
                comment_size, comment, faces))

        return (author, comment, faces)

    def parse_block_material(self, data, index):
        (children,) = BES.unpack("<I", data)
        logging.log(logging.VERBOSE, "{}Material ({} B) - Number of materials: {:08x}".format(
            " "*(index*2), len(data), children))

        res = self.parse_blocks({BES.BlockID.Standard : BES.BlockPresence.OptMultiple,
                    BES.BlockID.PteroMat  : BES.BlockPresence.OptMultiple},
                    data[4:], index + 1)

        if len(res[BES.BlockID.Standard]) + len(res[BES.BlockID.PteroMat]) != children:
            logging.error("{}Number of material children does not match".format(
                " "*(index*2)))

    def parse_block_standard(self, data, index):
        (unk1, unk2, bType) = BES.unpack("<I4sI", data)
        sPrint = "{}Standard ({} B) - unk1: {}, unk2: {}".format(
            " "*(index*2), len(data), unk1, unk2)
        ptr = 12
        for mapID in range(32):
            if bType & (1 << mapID):
                if mapID < len(BES.Standard.maps):
                    if BES.Standard.maps[mapID] == "UNKNOWN":
                        logging.warning("Undocumented bitmap detected")

                    (name_size, coord) = BES.unpack("<II", data[ptr:])
                    (name,) = BES.unpack("<" + str(name_size) + "s", data[ptr+8:])
                    sPrint += "\n{}{} map: ({}): {}".format(
                        " "*((index+1)*2), BES.Standard.maps[mapID],
                        name_size, pchar_to_string(name))
                    if coord & 0x5:
                        if coord & 0x5 == 0x1:
                            sPrint += ", U tile"
                        elif coord & 0x5 == 0x4:
                            sPrint += ", U mirror"
                        else:
                            logging.error("Unknown coordinates settings {:08x} not supported".
                                format(coord))
                    if coord & 0xA:
                        if coord & 0xA == 0x2:
                            sPrint += ", V tile"
                        elif coord & 0xA == 0xA:
                            sPrint += ", V mirror"
                        else:
                            logging.error("Unknown coordinates settings {:08x} not supported".
                                format(coord))
                    ptr += 8 + name_size
                else:
                    logging.error("Unknown bitmap {:08x} not supported".format(1 << mapID))
        if ptr != len(data):
            logging.error("Block size do not match")

        logging.log(logging.VERBOSE, sPrint)

    def parse_block_ptero_mat(self, data, index):
        (tSides, pType, collisMat, transType, veget) = BES.unpack("<II4sI4s", data)
        (name_size,) = BES.unpack("<I", data[20:])
        (name,) = BES.unpack("<" + str(name_size) + "s", data[24:])

        if tSides & 0xFFFFFFE:
            logging.warning("Invalid transparent sides settings: {:08x}".format(tSides))
        if collisMat[2:] != b'\x00\x00':
            logging.warning("Expected two zeros in collision material")
        if veget[2:] != b'\x00\x00':
            logging.warning("Expected two zeros in grow/grass type")

        sPrint = ("{}PteroMat ({} B) - name({}): {}, {}-Sided, collision material: '{}{}'" +
            ", grow type: '{}', grass type: '{}'").format(
            " "*(index*2), len(data), name_size, pchar_to_string(name), tSides + 1,
            chr(collisMat[0]), chr(collisMat[1]), chr(veget[0]), chr(veget[1]))
        if transType not in BES.PteroMat.transparency:
            logging.warning("Unknown transparency type {:08x}".format(transType))
        else:
            sPrint += ", transparency '{}'".format(BES.PteroMat.transparency[transType])

        ptr = 24 + name_size
        # TODO check for multiple texture instances of same type
        for texID in range(32):
            if pType & (1 << texID):
                if (texID >= BES.PteroMat.offset) and \
                (texID < BES.PteroMat.offset + len(BES.PteroMat.texs)):
                    (dataSize, sPrintNew) = BES.PteroMat.parseTexture(data[ptr:],
                                    index + 1, texID)
                    ptr += dataSize
                    sPrint += sPrintNew
                else:
                    logging.error("Unknown texture {:08x} not supported".format(1 << texID))

        logging.log(logging.VERBOSE, sPrint)

        if ptr != len(data):
            logging.error("Block size do not match")

def savePreview(imageData, besName):
    from PIL import Image

    img = Image.new('RGB', (64, 64), 'white')

    for row in range(0, 64):
        for col in range(0, 64):
            b = imageData[row*192+col*3+0]
            g = imageData[row*192+col*3+1]
            r = imageData[row*192+col*3+2]

            img.putpixel((col, row), (r, g, b))

    img.save(besName + ".png", 'PNG')

def processFile(fileName, extract):
    logging.info("Model: " + fileName)
    try:
        data = open(fileName, "rb").read()
        bes = BES(data)
        if not bes.parse_header():
            return
        preview = bes.parse_preview()
        if extract:
            savePreview(preview, fileName)
        else:
            bes.parse_data()
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    level = logging.INFO

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--check",
        help="check CHECK for integrity (as per reverse-engineered specification)",
        nargs="+")
    parser.add_argument("-x", "--extract-preview",
        help="extract preview image from EXTRACT_PREVIEW file",
        nargs="?")
    parser.add_argument("-v", "--verbose",
        help="verbose mode ON",
        action="store_true")
    args = parser.parse_args()

    if args.verbose:
        level = logging.VERBOSE

    logging.basicConfig(level=level, format="%(message)s")

    if not (args.check or args.extract_preview):
        parser.print_help()
        sys.exit(1)

    if args.check:
        for fileName in args.check:
            processFile(fileName, False)

    if  args.extract_preview:
        processFile(args.extract_preview, True)

