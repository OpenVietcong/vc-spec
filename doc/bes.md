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

### Unknown
| Offset | Name    | Type     |
|--------|---------|----------|
| 0      | Unknown | UINT32LE |
| 4      | Offset  | UINT32LE |

1. Usually 0x70
2. Offset to 'Unknown' block

### User info

Total size: 76 + comment length

Space between 'Name' and 'Comment' is filled with zeros


| Offset | Name           | Type     |
|--------|----------------|----------|
| 0      | Name length    | UINT32LE |
| 4      | Comment length | UINT32LE |
| 8      | Unknown        | UINT32LE |
| 12     | Name           | CHAR[]   |
| 76     | Comment        | CHAR[]   |

1. Length of 'Name' string. Should not exceed 64 bytes.
2. Length of 'Comment' string.
3. Unknown
4. Name (max 64)
5. Comment

### Unknown
Offset of 'Unknown' block points here.

### Object information

Total size: unknown

| Offset | Name          | Type     |
|--------|---------------|----------|
| 0      | Parent length | UINT32LE |
| 4      | Parent        | CHAR[]   |
| -      | Unknown       | CHAR[]   |
| -      | Name length   | UINT32LE |
| -      | Name          | CHAR[]   |

1. Length of parent's name
2. Parent's name
3. Unknown
4. Name length
5. Name

### Data
