This document describes BES files.

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
| 4      | Version   | CHAR[5]  |
| 9      | Unknown   | UINT32LE |
| 13     | Unknown   | CHAR[3]  |

1. Signature identifying the BES file. Contains fixed string 'BES' with NULL character at the end (0x42 0x45 0x53 0x00).
2. Version of this BES file. VietCong knows following versions:
  - 0004 (0x30 0x30 0x30 0x34 0x00)
  - 0005 (0x30 0x30 0x30 0x35 0x00)
  - 0006 (0x30 0x30 0x30 0x36 0x00)
  - 0007 (0x30 0x30 0x30 0x37 0x00)
  - 0008 (0x30 0x30 0x30 0x38 0x00)
  - 0100 (0x30 0x31 0x30 0x30 0x00)
3. Unknown word (or four chars?).
4. Unknown (always zeros).

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

Here is quick reference table of known data sub-blocks:

| Block Name    | Label |
|---------------|-------|
| Object        | 0x001 |
| ...           | ....  |
| Unknown 0x030 | 0x030 |
| Mesh          | 0x031 |
| Vertices      | 0x032 |
| Faces         | 0x033 |
| Properties    | 0x034 |
| Unknown 0x035 | 0x035 |
| Unknown 0x036 | 0x036 |
| ...           | ...   |
| Unknown 0x038 | 0x038 |
| ...           | ...   |
| User Info     | 0x070 |
| ...           |       |
| Unknown 0x100 | 0x100 |

### Object

| Offset | Name            | Type     |
|--------|-----------------|----------|
| 0      | Label           | UINT32LE |
| 4      | Blok size       | UINT32LE |
| 8      | Object children | UINT32LE |
| 12     | Name length     | UINT32   |
| 16     | Name            | CHAR[]   |

1. Label of this sub-block - always 0x001
2. Size of this sub-block (including this field and label)
3. Number of children objects inside of this one
4. Length of 'Name' string
5. Name

Other data sub-blocks may follow. Known sub-blocks:
* Object
* Unknown 0x030
* Unknown 0x100

### Unknown 0x030

| Offset | Name          | Type     |
|--------|---------------|----------|
| 0      | Label         | UINT32LE |
| 4      | Blok size     | UINT32LE |
| 8      | Mesh children | UINT32LE |

1. Label of this sub-block - always 0x030
2. Size of this sub-block (including this field and label)
3. Number of children meshes inside of this block

Other data sub-blocks may follow. Known sub-blocks:
* Mesh
* Properties
* Unknown 0x035
* Unknown 0x036

### Mesh

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Mesh ID   | UINT32LE |

1. Label of this sub-block - always 0x031
2. Size of this sub-block (including this field and label)
3. ID usually in interval <0;total-meshes) or 0xFFFFFFFF

Other data sub-blocks may follow. Known sub-blocks:
* Vertices
* Faces

### Vertices

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |
| 8      | Vertices count | UINT32LE |
| 12     | Size of vertex | UINT32LE |
| 16     | Unknown        | UINT32LE |

1. Label of this sub-block - always 0x032
2. Size of this sub-block (including this field and label)
3. Number of vertices in this data block
4. Size of vertex structure
5. Unknown - usually 0x12

Vertices data structures follows:

| Offset | Name       | Type      |
|--------|------------|-----------|
| 0      | Position x | FLOAT32LE |
| 4      | Position y | FLOAT32LE |
| 8      | Position z | FLOAT32LE |
| 12     | Unknown    | CHAR[]    |

1. 'X' vertex coordinate.
2. 'Y' vertex coordinate.
3. 'Z' vertex coordinate.
4. Unknown

### Faces

This block contains object faces.
Every face is made of 3 vertices (a, b, c).
Vertex value points to vertex ID in Vertices data block.

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Label       | UINT32LE |
| 4      | Blok size   | UINT32LE |
| 8      | Faces count | UINT32LE |

1. Label of this sub-block - always 0x033
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

1. Label of this sub-block - always 0x034
2. Size of this sub-block (including this field and label)
3. Length of 'Text' string
4. String containing user defined properties

### Unknown 0x035

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | CHAR[]   |

1. Label of this sub-block - always 0x035
2. Size of this sub-block (including this field and label)
3. Unknown

### Unknown 0x036

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x036
2. Size of this sub-block (including this field and label)
3. Unknown

### Unknown 0x038

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | CHAR[]   |

1. Label of this sub-block - always 0x038
2. Size of this sub-block (including this field and label)
3. Unknown

### User info

Space between 'Name' and 'Comment' is filled with zeros


| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |
| 8      | Name length    | UINT32LE |
| 12     | Comment length | UINT32LE |
| 16     | Unknown        | UINT32LE |
| 20     | Name           | CHAR[]   |
| 84     | Comment        | CHAR[]   |

1. Label of this sub-block - always 0x070
2. Size of this sub-block (including this field and label)
3. Length of 'Name' string. Should not exceed 64 bytes.
4. Length of 'Comment' string.
5. Unknown
6. Name (max 64)
7. Comment

### Unknown 0x100

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x100
2. Size of this sub-block (including this field and label)
3. Unknown
