This document describes CBF files.

File format
===========

Header
------

Total size: 32

| Offset | Name         | Type          |
|--------|--------------|---------------|
| 0      | Signature    | CHAR[8]       |
| 8      | File size    | UINT32LE      |
| 12     | Unknown      | UINT32LE[2]   |
| 20     | Table offset | UINT32LE      |
| 24     | Unknown      | UINT32LE      |
| 28     | Table size   | UINT32LE      |
