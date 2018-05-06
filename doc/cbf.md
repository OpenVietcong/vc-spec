This document describes CBF files.

Header
======

Total size: 32

| Offset | Name         | Type          |
|--------|--------------|---------------|
| 0      | Signature    | CHAR[8]       |
| 8      | Archive size | UINT32LE      |
| 12     | Reserved     | UINT32LE      |
| 16     | File count   | UINT32LE      |
| 20     | Table offset | UINT32LE      |
| 24     | Reserved     | UINT32LE      |
| 28     | Table size   | UINT32LE      |

1. Signature identifying the CBF file.
Contains fixed string "BIGF"\1"ZBL" without NULL character at the end (0x42 0x49 0x47 0x46 0x01x 0x5A 0x42 0x4C).
2. Size of CBF archive (including this header).
3. Reserved (always zeros).
4. Number of files in CBF archive.
5. Offset of Table of Files in CBF archive.
6. Reserved (always zeros).
7. Size of Table of Files.

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
| 4      | Unknown1        | UINT32LE[4] |
| 20     | File size       | UINT32LE    |
| 24     | Unknown2        | UINT32LE    |
| 28     | Compressed size | UINT32LE    |
| 32     | Storage type    | UINT32LE    |
| 36     | Unknown3        | UINR32LE    |
| 40     | File name       | CHAR[]      |

1. Offset of stored file in CBF archive.
2. Unknown
3. File size after extraction
4. Unknown
5. File size in the CBF archive in case of compression as a storage method.
Otherwise zero.
6. Storage method - describes how is file stored in CBF archive:
  - 0x0 file is encrypted.
  - 0x1 file is compressed.
7. Unknown.
8. File name with NULL character.
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

