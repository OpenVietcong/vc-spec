This document describes MANM (Model animation?) files.

File format
===========

This file is made of:
* Header
* Data

Header
------

Total size: 16

| Offset | Name      | Type     |
|--------|-----------|----------|
| 0      | Signature | CHAR[4]  |
| 4      | Unknown   | UINT32LE |
| 8      | Objects   | UINT32LE |
| 12     | Unknown   | UINT32LE |

1. Signature identifying the MANM file.
Contains fixed string 'MANM' (0x4D 0x41 0x4E 0x4D).
Not NULL-terminated
2. Unknown (always 0x00000001)
3. Number of objects
4. Unknown (always 0x00000000)

Data
----

Data block contains several *Object* sub-blocks.
Each *Object* contains other 3 kinds of transformations.

### Object

| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Label          | UINT32LE |
| 4      | Block size     | UINT32LE |
| 8      | Translation cnt| UINT32LE |
| 12     | Rotation cnt   | UINT32LE |
| 16     | Unknown3 cnt   | UINT32LE |
| 20     | Unknown        | UINT32LE |
| 24     | Duration       | UINT32LE |
| 28     | Unknown        | UINT32LE |
| 32     | Name           | CHAR[]   |

1. Label of this sub-block - always 0x01
2. Size of this sub-block (including this field and label)
3. Number of *Translation* sub-blocks
4. Number of *Rotation* sub-blocks
5. Number of *Unknown3* sub-blocks
6. Unknown
7. Animation time duration
8. Unknown
9. Mesh name from BES file which will be animated

Other data sub-blocks may follow. Known sub-blocks:
* Translation block
* Rotation block
* Unknown3 block

### Translation

| Offset | Name       | Type      |
|--------|------------|-----------|
| 0      | Label      | UINT32LE  |
| 4      | Start time | UINT32LE  |
| 8      | Position x | FLOAT32LE |
| 12     | Position y | FLOAT32LE |
| 16     | Position z | FLOAT32LE |

1. Label of this sub-block - always 0x01
2. Start time for this transformation
3. Position X
4. Position Y
5. Position Z

### Rotation

| Offset | Name       | Type      |
|--------|------------|-----------|
| 0      | Label      | UINT32LE  |
| 4      | Start time | UINT32LE  |
| 8      | Unknown    | FLOAT32LE |
| 12     | Unknown    | FLOAT32LE |
| 16     | Unknown    | FLOAT32LE |
| 20     | Unknown    | FLOAT32LE |

1. Label of this sub-block - always 0x02
2. Start time for this transformation
3. Unknown
4. Unknown
5. Unknown
6. Unknown

### Unknown3

| Offset | Name       | Type      |
|--------|------------|-----------|
| 0      | Label      | UINT32LE  |
| 4      | Start time | UINT32LE  |
| 8      | Unknown    | FLOAT32LE |
| 12     | Unknown    | FLOAT32LE |
| 16     | Unknown    | FLOAT32LE |

1. Label of this sub-block - always 0x03
2. Start time for this transformation
3. Unknown
4. Unknown
5. Unknown

