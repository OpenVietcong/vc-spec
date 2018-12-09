This document describes SCO (Scene Object?) files.

File format
===========

* all strings are NON-terminated by NULL characters

First known bytes starts at offset 0x64, where is stored number of used BES files and their names:

| Offset | Label | Type     |
|--------|-------|----------|
| 0      | Count | UINT32LE |

1. Number of BES files.

BES file data structure follows (for each file):

| Offset | Name        | Type     |
|--------|-------------|----------|
| 0      | File length | UINT32LE |
| 4      | File name   | CHAR[]   |

1. Length of 'File name' field
2. BES file name.

After this list follows unknown information (TLV encoding) about each mesh of each BES file, probably also with transformation informations.

