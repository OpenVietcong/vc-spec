This document describes BES (BenyErikSolitude) files.

File format
===========

* all strings are terminated by NULL characters
* length of every string includes NULL character
* some data structures are inspired by D3D8.
For detailed definition of some structures mentioned in this file see
[d3dtypes.h](https://github.com/wine-mirror/wine/blob/master/include/d3dtypes.h)
file of Wine project.

This file is made of:
* Header
* Preview
* Data

Header
------

Total size: 16

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Signature | CHAR[4]  |
| 4      | Version   | CHAR[4]  |
| 8      | Unknown   | UINT32LE |
| 12     | Unknown   | UINT32LE |

1. Signature identifying the BES file. Contains fixed string 'BES' with NULL character at the end (0x42 0x45 0x53 0x00).
2. Version of this BES file. VietCong knows following versions:
  - 0004 (0x30 0x30 0x30 0x34)
  - 0005 (0x30 0x30 0x30 0x35)
  - 0006 (0x30 0x30 0x30 0x36)
  - 0007 (0x30 0x30 0x30 0x37)
  - 0008 (0x30 0x30 0x30 0x38)
  - 0100 (0x30 0x31 0x30 0x30)
3. Unknown
4. Unknown

Preview
-------

Total size: 12288 (0x3000)

This block contains preview image made by 3D modelling tool.
Preview image is made of 64x64 pixels, where every pixel is the following format:

| Offset | Name      | Type  |
|--------|-----------|-------|
| 0      | Green     | UINT8 |
| 1      | Blue      | UINT8 |
| 2      | Red       | UINT8 |

Data
----

Data block contains several sub-blocks.
Each sub-block contain it's label, size and data itself.
Some sub-blocks may contain other sub-blocks inside.
Their occurence frequency is written in brackets.

Here is quick reference table of known data sub-blocks:

| Block Name     | Label  |
|----------------|--------|
| Object         | 0x0001 |
| ...            | ...    |
| Model          | 0x0030 |
| Mesh           | 0x0031 |
| Vertices       | 0x0032 |
| Faces          | 0x0033 |
| Properties     | 0x0034 |
| Transformation | 0x0035 |
| Unknown 0x036  | 0x0036 |
| ...            | ...    |
| Unknown 0x038  | 0x0038 |
| ...            | ...    |
| User Info      | 0x0070 |
| ...            | ...    |
| Material       | 0x1000 |
| Standard       | 0x1001 |
| PteroMat       | 0x1002 |

### Object

| Offset | Name            | Type     |
|--------|-----------------|----------|
| 0      | Label           | UINT32LE |
| 4      | Blok size       | UINT32LE |
| 8      | Object children | UINT32LE |
| 12     | Name length     | UINT32   |
| 16     | Name            | CHAR[]   |

1. Label of this sub-block - always 0x0001
2. Size of this sub-block (including this field and label)
3. Number of 'Object' sub-blocks inside of this one
4. Length of 'Name' string
5. Name

Other data sub-blocks may follow. Known sub-blocks:
* Object (any)
* Model (1 at most)
* Properties (1 at most)
* Transformation (1 at most)
* Unknown 0x038 (1 at most)
* Material (1 at most)

### Model

| Offset | Name          | Type     |
|--------|---------------|----------|
| 0      | Label         | UINT32LE |
| 4      | Blok size     | UINT32LE |
| 8      | Mesh children | UINT32LE |

1. Label of this sub-block - always 0x0030
2. Size of this sub-block (including this field and label)
3. Number of children meshes inside of this block

Other data sub-blocks may follow. Known sub-blocks:
* Mesh (any)
* Properties (1)
* Transformation (1)
* Unknown 0x036 (1 at most)

### Mesh

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Material  | UINT32LE |

1. Label of this sub-block - always 0x0031
2. Size of this sub-block (including this field and label)
3. Material ID (popints to the one of children of 'Material' data block) used by this mesh.
Value 0xFFFFFFFF if no material is used.

Other data sub-blocks may follow. Known sub-blocks:
* Vertices (1)
* Faces (1)

### Vertices

This block contains mesh vertices, which are heavily inspired by D3D8.

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Vertices  | UINT32LE |
| 12     | Size      | UINT32LE |
| 16     | Flags     | UINT32LE |

1. Label of this sub-block - always 0x0032
2. Size of this sub-block (including this field and label)
3. Number of vertices in this data block
4. Size of vertex structure.
Should be 24 + 8 * number\_of\_textures (see below).
5. Vertex flags (*D3DFVF*).
BES supports following flags only (all of these flags must be set):
 * D3DFVF\_XYZ (0x002)
 * D3DFVF\_NORMAL (0x010)
 * D3DFVF\_TEXn (0x000 - 0x800) - number of textures used by material (see 'Type' field of Standard or PteroMat).
Note that some materials (Standard for example) may contain more textures than PteroEngine/D3D allows (D3DFVF\_TEX8) - that case should be avoided.

Vertices data structures follows.
This structure is based on *D3DVERTEX*, with difference in uv coords (see below) :

| Offset | Name      | Type        |
|--------|-----------|-------------|
| 0      | x coord   | FLOAT32LE   |
| 4      | y coord   | FLOAT32LE   |
| 8      | z coord   | FLOAT32LE   |
| 12     | x normal  | FLOAT32LE   |
| 16     | y normal  | FLOAT32LE   |
| 20     | z normal  | FLOAT32LE   |
| 24     | uv coords | FLOAT32LE[] |

1. 'X' vertex homogeneous coordinate.
2. 'Y' vertex homogeneous coordinate.
3. 'Z' vertex homogeneous coordinate.
4. 'X' vertex normal coordinate.
5. 'Y' vertex normal coordinate.
6. 'Z' vertex normal coordinate.
7. 'UV' vertex texture coordinates.
Contains two float coordinates ('U' and 'V') for each texture (see vertices 'Flags' for number of textures).

### Faces

This block contains object faces.
Every face is made of 3 vertices (a, b, c).
Vertex value points to vertex ID in 'Vertices' data block.

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Label       | UINT32LE |
| 4      | Blok size   | UINT32LE |
| 8      | Faces count | UINT32LE |

1. Label of this sub-block - always 0x0033
2. Size of this sub-block (including this field and label)
3. Number of faces in this data block

Faces data structures follows (size of each structure is 12 bytes):

| Offset | Name     | Type     |
|--------|----------|----------|
| 0      | Vertex a | UINT32LE |
| 4      | Vertex b | UINT32LE |
| 8      | Vertex c | UINT32LE |

1. Vertex 'a'
2. Vertex 'b'
3. Vertex 'c'

### Properties

This block contains User defined properties (as known from 3D Studio Max).
Purpose of these properties is unknown.

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Label       | UINT32LE |
| 4      | Blok size   | UINT32LE |
| 8      | Text length | UINT32LE |
| 12     | Text        | CHAR[]   |

1. Label of this sub-block - always 0x0034
2. Size of this sub-block (including this field and label)
3. Length of 'Text' string
4. String containing user defined properties

### Transformation

This block contains transformation informations: translation, rotation and scale.
Also the transformation matrix 4x4 is located here (which is redundant to previous vectors).
This matrix is in some files computed wrong and thus contains significant error.

| Offset | Name        | Type          |
|--------|-------------|---------------|
| 0      | Label       | UINT32LE      |
| 4      | Blok size   | UINT32LE      |
| 8      | Translation | FLOAT32LE[3]  |
| 20     | Rotation    | FLOAT32LE[3]  |
| 32     | Scale       | FLOAT32LE[3]  |
| 44     | Matrix      | FLOAT32LE[16] |

1. Label of this sub-block - always 0x0035
2. Size of this sub-block (including this field and label) - always 0x6C (108B)
3. Object translation in scene (*D3DVECTOR*)
4. Object rotation (in radians) in scene (*D3DVECTOR*)
5. Object scale (*D3DVECTOR*)
6. Transformation matrix (*D3DMATRIX*)

### Unknown 0x036

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x0036
2. Size of this sub-block (including this field and label) - always 0xC (12B)
3. Unknown

### Unknown 0x038

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | CHAR[]   |

1. Label of this sub-block - always 0x0038
2. Size of this sub-block (including this field and label)
3. Unknown

### User info

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |
| 8      | Name length    | UINT32LE |
| 12     | Comment length | UINT32LE |
| 16     | Unknown        | UINT32LE |
| 20     | Name           | CHAR[64] |
| 84     | Comment        | CHAR[]   |

1. Label of this sub-block - always 0x0070
2. Size of this sub-block (including this field and label)
3. Length of 'Name' string. Should not exceed 64 bytes.
4. Length of 'Comment' string.
5. Unknown
6. Name (max 64 - remaining bytes are filled by zero)
7. Comment

### Material

| Offset | Name              | Type     |
|--------|-------------------|----------|
| 0      | Label             | UINT32LE |
| 4      | Block size        | UINT32LE |
| 8      | Material children | UINT32LE |

1. Label of this sub-block - always 0x1000
2. Size of this sub-block (including this field and label)
3. Number of materials inside of this block

Other data sub-blocks may follow. Known sub-blocks:
* Standard (any)
* PteroMat (any)

### Standard

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Label       | UINT32LE |
| 4      | Block size  | UINT32LE |
| 8      | Unknown1    | UINT32LE |
| 12     | Unknown2    | UINT32LE |
| 16     | Type        | UINT32LE |

1. Label of this sub-block - always 0x1001
2. Size of this sub-block (including this field and label)
3. Unknown
4. Unknown
5. Map type bitfield.
Here is a list of maps contained in this material.
Unfortunatelly, map flags in this structure have different order than UV maps in 'Vertices' block.
For this reason, the maps here are ordered according to order in 'Vertices' block and the flag value is written in brackets.
Also note that 3DS Max allows to create 'Opacity' texture, but it is never exported into BES file.
There is also unused flag 0x100, which may (or may not) be associated with 'Opacity' - probably misstake by Ptero developers:
  * 1  - Ambient Color     (0x008)
  * 2  - Diffuse Color     (0x001)
  * 3  - Specular Color    (0x010)
  * 4  - Specular Level    (0x020)
  * 5  - Glossiness        (0x040)
  * 6  - Self-Illumination (0x080)
  * 7  - Filter Color      (0x200)
  * 8  - Bump              (0x004)
  * 9  - Reflection        (0x400)
  * 10 - Refraction        (0x800)
  * 11 - Displacement      (0x002)

Set bit in field 'Type' indicates that material contains appropriate map.
All maps have the same structure:

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Name length | UINT32LE |
| 4      | Coordinates | UINT32LE |
| 8      | Name        | CHAR[]   |

1. Length of 'Name' string
2. Coordinates configuration bitfield.
Tile and mirror can not be used at the same time.
  *  0 - U tile
  *  1 - V tile
  *  2 - U mirror
  *  3 - V mirror
3. Name of bitmap file

### PteroMat

| Offset | Name         | Type     |
|--------|--------------|----------|
| 0      | Label        | UINT32LE |
| 4      | Block size   | UINT32LE |
| 8      | Sides        | UINT32LE |
| 12     | Type         | UINT32LE |
| 16     | CollisionMat | CHAR[4]  |
| 20     | Transparency | UINT32LE |
| 24     | Vegetation   | CHAR[4]  |
| 28     | Name length  | UINT32LE |
| 32     | Name         | CHAR[]   |

1. Label of this sub-block - always 0x1002
2. Size of this sub-block (including this field and label)
3. Number of material sides: 0 = 1 sided, 1 = 2-sided. Other values are invalid.
4. Texture type bitfield. Here is a sorted list of textures contained in this material:
  * 16 - Diffuse #1 - Ground
  * 17 - Diffuse #2 - Multitexture
  * 18 - Diffuse #3 - Overlay
  * 19 - Environment #1
  * 20 - LightMap
  * 21 - Unknown
  * 22 - Environment #2
  * 23 - LightMap (Engine Lights)
5. Collision Material (only first 2 bytes are valid, the rest are zeros)
6. Transparency type. Description can be found at
[vietcong.info](http://www.vietcong.info/portal/forum/viewthread.php?thread_id=344&pid=4749#post_4749):
  * 0x202D: - none - (opaque)
  * 0x3023: #0 - transparent, zbufwrite, sort
  * 0x3123: #1 - transparent, zbufwrite, sort, 1-bit alpha
  * 0x3223: #2 - translucent, no\_zbufwrite, sort
  * 0x3323: #3 - transparent, zbufwrite, nosort, 1-bit alpha
  * 0x3423: #4 - translucent, add with background, no\_zbufwrite, sort
  * other: unknown
7. Grow/Grass Type (only first 2 **bytes** are valid, the rest are zeros)
  * 0 - Grow Type
  * 1 - Grass Type
8. Length of 'Name' string
9. Material name

Set bit in field 'Type' indicates that PteroMat contains appropriate texture.
All textures have the same structure:

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Coordinates | UINT32LE |
| 4      | Name length | UINT32LE |
| 8      | Name        | CHAR[]   |

1. Coordinates configuration bitfield.
Upper 2 bytes should be equal to PteroMat's 'Type' field (but it is not always true - probably due some bug in 3DS Max).
Meaning of lower 2 bytes follows (all bits except those listed here are always zero):
  * 0 - U tile
  * 1 - V tile
  * 4 - unknown
2. Length of 'Name' string
3. Name of texture file

