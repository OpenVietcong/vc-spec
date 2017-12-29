This document describes BES files.

File format
===========

* all strings are terminated by NULL characters
* length of every string includes NULL character

This file is made of:
* Header
* Unkown
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

Unknown
-------

This block is optional and its size depends on BES version.

Total size: 0 - 12288 (0x3000)

This block usually contains 0x7D bytes.

Data
----

Data block contains several sub-blocks.
Each sub-block contain it's label, size and data itself.

Here is quick reference table of known data sub-blocks:

| Block Name | Label |
|------------|-------|
| Mesh       | 0x01  |
| ...        | ....  |
| Unknown 30 | 0x30  |
| Unknown 31 | 0x31  |
| Vertices   | 0x32  |
| Faces      | 0x33  |
| Unknown 34 | 0x34  |
| Unknown 35 | 0x35  |
| Unknown 36 | 0x36  |
| ...        | ...   |
| User Info  | 0x70  |
| ...        |       |

### Mesh

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |
| 8      | Mesh children  | UINT32LE |
| 12     | Name length    | UINT32   |
| 16     | Name           | CHAR[]   |

1. Label of this sub-block - always 0x01
2. Size of this sub-block (including this field and label)
3. Number of children meshes inside of this mesh
4. Length of 'Name' string
5. Name

Other data sub-blocks may follow. Known sub-blocks:
* Mesh
* Unknown 0x30

### Unknown 0x30

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x30
2. Size of this sub-block (including this field and label)
3. Unknown

Other data sub-blocks may follow. Known sub-blocks:
* Unknown 0x31
* Unknown 0x34
* Unknown 0x35
* Unknown 0x36

### Unknown 0x31

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x31
2. Size of this sub-block (including this field and label)
3. Unknown - usually 0xFFFFFFFF

Other data sub-blocks may follow. Known sub-blocks:
* Vertices
* Faces

### Vertices

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |

1. Label of this sub-block - always 0x32
2. Size of this sub-block (including this field and label)

### Faces

This block contains object faces.
Every face is made of 3 vertices (a, b, c), therefore number of vertices should be divisible by number 3.
Vertex value points to vertex ID in Vertices data block

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Blok size      | UINT32LE |
| 8      | Vertices count | UINT32LE |
| 12     | Vertex 1a      | UINT32LE |
| 16     | Vertex 1b      | UINT32LE |
| 20     | Vertex 1c      | UINT32LE |
| 24     | Vertex 2a      | UINT32LE |
| 28     | Vertex 2b      | UINT32LE |
| 32     | Vertex 2c      | UINT32LE |
| ...    | ...            | ...      |

1. Label of this sub-block - always 0x33
2. Size of this sub-block (including this field and label)
3. Number of vertices in this data block
4. Vertex 'a' for face '1'
5. Vertex 'b' for face '1'
6. Vertex 'c' for face '1'
7. Vertex 'a' for face '2'
8. Vertex 'b' for face '2'
9. Vertex 'c' for face '2'
10. ...

### Unknown 0x34

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | CHAR[]   |

1. Label of this sub-block - always 0x34
2. Size of this sub-block (including this field and label)
3. Unknown

### Unknown 0x35

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | CHAR[]   |

1. Label of this sub-block - always 0x35
2. Size of this sub-block (including this field and label)
3. Unknown

### Unknown 0x36

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Label     | UINT32LE |
| 4      | Blok size | UINT32LE |
| 8      | Unknown   | UINT32LE |

1. Label of this sub-block - always 0x36
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

1. Label of this sub-block - always 0x70
2. Size of this sub-block (including this field and label)
3. Length of 'Name' string. Should not exceed 64 bytes.
4. Length of 'Comment' string.
5. Unknown
6. Name (max 64)
7. Comment
