This document describes CBF (CompressedBigFile), the pointer-base file format.
There are two known versions of CBF: *ZBL0* (ZblekaSoft) and *ZBL1*.
*ZBL0* uses plain file tables and files itself (these may also be compressed,
like in case of *ZBL1*), while *ZBL1* uses encryption for both file tables and files
(although it uses different encryption algorithm for each).
*ZBL1* also stores size of each file descriptor (which make reading of such file
descriptor easier), while *ZBL0* does not.
For the second version of CBF, we distinguish between two modes:
lets call them *classic* and *extended*.
They differ in meaning of few entries.

Header
======

Total size: 52 or bigger

| Offset | Name         | Type          |
|--------|--------------|---------------|
| 0      | Signature    | CHAR[4]       |
| 4      | Version      | CHAR[4]       |
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
Contains fixed string "BIGF" (0x42 0x49 0x47 0x46) - probably stands for *BigFile*.
2. CBF version. Currently known two versions:
  * \0"ZBL" (0x00x 0x5A 0x42 0x4C). Probably stands for
[ZblekaSoft](https://web.archive.org/web/20050321050830/http://www.zbl.cz/).
  * \1"ZBL" (0x01x 0x5A 0x42 0x4C)
3. Size of CBF archive (including this header).
4. Reserved (always zeros).
5. Number of files in CBF archive.
6. Offset of Table of Files in CBF archive.
7. Reserved (always zeros).
8. Size of Table of Files.
9. Reserved (always zeros).
10. Header size. Always 64 for *ZBL0*, for *ZBL1* defines mode of CBF file:
  * 0: *classic* CBF, which means no extensions - header size is 52 in total (usually official Pterodon CBF/DAT files).
  * other: *extended* CBF and size of its header. 64 usually for DAT files, 70 and bigger usually CBF files.
11. Reserved (always zeros).
12. Two possible meanings:
  * *ZBL0* and *ZBL1 Extended*:
time of CBF creation represented as *FILETIME* - see
[windef.h](https://github.com/wine-mirror/wine/blob/master/include/windef.h)
for more details.
  * *ZBL1 Classic*: unknown.
13. Reserved (always zeros) - available for header size >= 64 only.
14. Label of this sub block - always 0x1 - this and following available for header size >= 70 only.
15. Length of Comment.
16. Comment without terminating NULL character
(HB for hradba folder, maps for maps folder, POKUS for setup.cbf).

Table of Files
==============

Table of Files consists of file descriptor for each file stored one by one.
For *ZBL1*, before every descriptor is stored its size.

Size of file descriptor (ZBL1 only)
-----------------------------------

Total size: 4

| Offset | Name            | Type     |
|--------|-----------------|----------|
| 0      | Descriptor size | UINT16LE |

1. Size of following descriptor

File descriptor
---------------

Descriptor of file in CBF archive.
For *ZBL1* version all fields are encrypted.

Total size: 40 + file name

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
  * *ZBL0* and *ZBL1 Extended*: unknown.
  * *ZBL1 Classic*: reserved (always zeros).
4. Two possible meanings:
  * *ZBL0* and *ZBL1 Extended*:
time of file creation represented as *FILETIME* structure.
  * *ZBL1 Classic*: reserved (always zeros).
5. File size after extraction
6. Reserved (always zeros).
7. File size in the CBF archive in case of compression as a storage method.
Otherwise zero.
8. Encoding method - describes how is file stored in CBF archive:
  * 0x0 file is not encoded (*ZBL0*) or is encrypted (*ZBL1*).
  * 0x1 file is compressed.
9. Unknown.
10. File name with NULL character.
For *ZBL1*, the length of the string can be calculated as "Descriptor size - 40".
Uses windows-1250 encoding.

Encryption of file descriptor (ZBL1 only)
-----------------------------------------

File descriptors are encrypted using simple symetric algorithm with *lut* (look-up table) and its *key*.
The *lut* has following values:
```
lut[16] = {
	0x32, 0xF3, 0x1E, 0x06, 0x45, 0x70, 0x32, 0xAA,
	0x55, 0x3F, 0xF1, 0xDE, 0xA3, 0x44, 0x21, 0xB4,
};
```

Data are (en/de)crypted byte by byte as (de/en)crypted value XORed with value from *lut*.
The *key* for *lut* is 8b wide and initialized with length of (de)coding data.
Every next step is *key* set to encrypted value from previous step.
Only lower 4b from *key* are used for indexing *lut*, since *key* is 8b and *lut*
has size of 16 values (4b index).

Here is algorithm for decryption:
```
dec_val = enc_val ^ lut[key & 0xF];
key = enc_val;
```
Files
=====

Files stored in CBF archive can be either plain (*ZBL0* only), encrypted (*ZBL1* only) or compressed (both *ZBL0* and *ZBL1*).

Encrypted files (ZBL1 only)
---------------------------

Files are encrypted using simple algorithm with static *salt* (0xA6) and file length as a *key*.
All values are 8b wide.

Here is algorithm for decryption:
```
dec_val = (enc_val + salt + key) ^ key;
```

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

