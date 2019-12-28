This document describes CBF (CompressedBigFile) files.
We distinguish between two versions/modes of CBF:
lets call them *classic* and *extended*.
They differ in meaning of few entries.

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
| 44     | DateTime     | UINT32LE[2]   |
|      | (for header size >= 64) |      |
| 52     | Reserved     | UINT32LE[3]   |
|      | (for header size >= 70) |      |
| 64     | Label        | UINT16LE      |
| 66     | Comment size | UINT32LE      |
| 70     | Comment      | CHAR[]        |

1. Signature identifying the CBF file.
Contains fixed string "BIGF"\1"ZBL" without NULL character at the end (0x42 0x49 0x47 0x46 0x01x 0x5A 0x42 0x4C).
  * BIGF probably stands for *BigFile*
  * ZBL probably stands for
[ZblekaSoft](https://web.archive.org/web/20050321050830/http://www.zbl.cz/)
2. Size of CBF archive (including this header).
3. Reserved (always zeros).
4. Number of files in CBF archive.
5. Offset of Table of Files in CBF archive.
6. Reserved (always zeros).
7. Size of Table of Files.
8. Reserved (always zeros).
9. Extension header size. Defines version of CBF file:
  * 0: *classic* CBF (usually official Pterodon CBF/DAT files).
  * other: *extended* CBF and size of its header. 64 usually for DAT files, 70 and bigger usually CBF files.
10. Reserved (always zeros).
11. Two meanings:
  * *Classic* CBF: unknown.
  * *Extended* CBF: time of CBF creation represented as *FILETIME* - see
[windef.h](https://github.com/wine-mirror/wine/blob/master/include/windef.h)
for more details.
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
| 8      | Unknown1        | UINT32LE    |
| 12     | DateTime        | UINT32LE[2] |
| 20     | File size       | UINT32LE    |
| 24     | Reserved        | UINT32LE    |
| 28     | Compressed size | UINT32LE    |
| 32     | Encoding        | UINT32LE    |
| 36     | Unknown2        | UINT32LE    |
| 40     | File name       | CHAR[]      |

1. Offset of stored file in CBF archive.
2. Reserved (always zeros).
3. Two meanings:
  * *Classic* CBF: reserved (always zeros).
  * *Extended* CBF: unknown.
4. Two meanings:
  * *Classic* CBF: reserved (always zeros).
  * *Extended* CBF: time of file creation represented as *FILETIME* structure.
5. File size after extraction
6. Reserved (always zeros).
7. File size in the CBF archive in case of compression as a storage method.
Otherwise zero.
8. Encoding method - describes how is file stored in CBF archive:
  * 0x0 file is encrypted.
  * 0x1 file is compressed.
9. Unknown.
10. File name with NULL character.
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

