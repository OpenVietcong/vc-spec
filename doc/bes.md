This document describes BES (BenyErikSolitude) files.

File format
===========

* all strings are terminated by NULL characters
* length of every string includes NULL character

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
| Bitmap         | 0x1001 |
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

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Label       | UINT32LE |
| 4      | Blok size   | UINT32LE |
| 8      | Vertices    | UINT32LE |
| 12     | Size        | UINT32LE |
| 16     | Properties  | UINT32LE |

1. Label of this sub-block - always 0x0032
2. Size of this sub-block (including this field and label)
3. Number of vertices in this data block
4. Size of vertex structure.
Should be 24 + 8 * number\_of\_textures (see below).
5. Vertices properties.
Here is description of some **bytes** - bytes not listed here are always zero:
  * 0 - always 0x12
  * 1 - number of textures used by material (see 'Type' field of Bitmap or PteroMat).

Vertices data structures follows:

| Offset | Name       | Type        |
|--------|------------|-------------|
| 0      | Position x | FLOAT32LE   |
| 4      | Position y | FLOAT32LE   |
| 8      | Position z | FLOAT32LE   |
| 12     | Unknown    | FLOAT32LE   |
| 16     | Unknown    | FLOAT32LE   |
| 20     | Unknown    | FLOAT32LE   |
| 24     | UV mapping | FLOAT32LE[] |

1. 'X' vertex coordinate.
2. 'Y' vertex coordinate.
3. 'Z' vertex coordinate.
4. Unknown
5. Unknown
6. Unknown
7. UV mapping.
Contains two float coordinates ('U' and 'V') for each texture (see vertices 'Properties' for number of textures).

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

| Offset | Name        | Type          |
|--------|-------------|---------------|
| 0      | Label       | UINT32LE      |
| 4      | Blok size   | UINT32LE      |
| 8      | Translation | FLOAT32LE[3]  |
| 20     | Rotation    | FLOAT32LE[3]  |
| 32     | Scale       | FLOAT32LE[3]  |
| 44     | Unknown1    | FLOAT32LE[10] |
| 84     | Translation | FLOAT32LE[3]  |
| 96     | Unknown2    | FLOAT32LE[3]  |

1. Label of this sub-block - always 0x0035
2. Size of this sub-block (including this field and label) - always 0x6C (108B)
3. Object translation in scene - transformation values are in the following order: x, y, z
4. Object rotation (in radians) in scene - transformation values are in the following order: x, y, z
5. Object scale - transformation values are in the following order: x, y, z
6. Unknown
7. Same values as 3.
8. Unknown

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
* Bitmap (any)
* PteroMat (any)

### Bitmap

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
Here is a sorted list of maps contained in this bitmap:
  * 0 - Diffuse Color
  * 1 - Displacement
  * 2 - Bump
  * 3 - Ambient Color
  * 4 - Specular Color
  * 5 - Specular Level
  * 6 - Glossiness
  * 7 - Self-Illumination
  * 8 - Unknown
  * 9 - Filter Color
  * 10 - Reflection
  * 11 - Refraction

Set bit in field 'Type' indicates that bitmap contains appropriate map.
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
| 20     | Unknown      | UINT32LE |
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
6. Transparency type:
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

