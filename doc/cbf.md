This document describes CBF files.

Header
======

Total size: 52 (without extensions)

| Offset | Name         | Type          |
|--------|--------------|---------------|
| 0      | Signature    | CHAR[8]       |
| 8      | Archive size | UINT32LE      |
| 12     | Reserved     | UINT32LE      |
| 16     | File count   | UINT32LE      |
| 20     | Table offset | UINT32LE      |
| 24     | Reserved     | UINT32LE      |
| 28     | Table size   | UINT32LE      |
| 32     | Reserved     | UINT32LE      |
| 36     | Header size  | UINT32LE      |
| 40     | Reserved     | UINT32LE      |
| 44     | Unknown1     | UINT32LE[2]   |
|      | (for header size >= 64) |      |
| 52     | Reserved     | UINT32LE[3]   |
|      | (for header size >= 70) |      |
| 64     | Label        | UINT16LE      |
| 66     | Comment size | UINT32LE      |
| 70     | Comment      | CHAR[]        |

1. Signature identifying the CBF file.
Contains fixed string "BIGF"\1"ZBL" without NULL character at the end (0x42 0x49 0x47 0x46 0x01x 0x5A 0x42 0x4C).
2. Size of CBF archive (including this header).
3. Reserved (always zeros).
4. Number of files in CBF archive.
5. Offset of Table of Files in CBF archive.
6. Reserved (always zeros).
7. Size of Table of Files.
8. Reserved (always zeros).
9. Extension header size. 0 Means no extra data available (header size = 52), otherwise it means header size.
 * 70 (and bigger): usually CBF files.
 * 64: usually DAT files.
 * 0: others (usually official Pterodon CBF/DAT files).
10. Reserved (always zeros).
11. Unknown1
12. Reserved (always zeros) - available for header size >= 64 only.
13. Label of this sub block - always 0x1 - this and following available for header size >= 70 only.
14. Length of Comment (with terminating NULL character).
15. Comment (HB for hradba folder, maps for maps folder, POKUS for setup.cbf).

Table of Files
==============

Table of Files consists of file descriptor for each file stored one by one.
Before every descriptor is stored its size.

Size of file descriptor
-----------------------

Total size: 4

| Offset | Name            | Type     |
|--------|-----------------|----------|
| 0      | Descriptor size | UINT16LE |

1. Size of following descriptor

File descriptor
---------------

Descriptor of file in CBF archive.
All fields are encrypted.

Total size: Descriptor size

| Offset | Name            | Type        |
|--------|-----------------|-------------|
| 0      | File offset     | UINT32LE    |
| 4      | Reserved        | UINT32LE    |
| 8      | Unknown1        | UINT32LE[3] |
| 20     | File size       | UINT32LE    |
| 24     | Reserved        | UINT32LE    |
| 28     | Compressed size | UINT32LE    |
| 32     | Encoding        | UINT32LE    |
| 36     | Unknown2        | UINT32LE    |
| 40     | File name       | CHAR[]      |

1. Offset of stored file in CBF archive.
2. Reserved (always zeros).
3. Unknown
4. File size after extraction
5. Reserved (always zeros).
6. File size in the CBF archive in case of compression as a storage method.
Otherwise zero.
7. Encoding method - describes how is file stored in CBF archive:
  - 0x0 file is encrypted.
  - 0x1 file is compressed.
8. Unknown.
9. File name with NULL character.
Length of the string can be calculated as "Descriptor size - 40".
Uses windows-1250 encoding.

Files
=====

Files stored in CBF archive can be either encrypted or compressed.

Encrypted files
---------------

Compressed files
----------------

Compression is based on standard LZW algorithm.
LZW dictionary is initialized on 256 values (0-255) and end code (key 256), therefore key width is initialized on 9 bits.
LZW dictionary does not contain clear code, instead, the compressed file is divided into several blocks, where each block is decompressed separately.
Each block consists of its header (table below) and compressed data.

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | Signature   | CHAR[4]  |
| 4      | Input size  | UINT32LE |
| 8      | Output size | UINT32LE |

1. Signature identifying LZW block.
Contains fixed string "[..]" without NULL character at the end (0x5B 0x2E 0x2E 0x5D).
2. Input (compressed) size of LZW block.
3. Output (decompressed) size of LZW block.

