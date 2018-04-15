This document describes CBF files.

File format
===========

Header
------

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

