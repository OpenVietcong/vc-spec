This document describes BES files.

File format
===========

Header
------

Total size: 16

| Offset | Name      | Type          |
|--------|-----------|---------------|
| 0      | Signature | CHAR[4]       |
| 4      | Version   | CHAR[4]       |
| 8      | Unknown   | UINT32LE[2]   |

1. Signature identifying the BES file. Contains fixed string 'BES' with NULL character at the end (0x42 0x45 0x53 0x00).
2. Version of this BES file. VietCong knows following versions (note that version number is in ASCII without NULL character at the end):
  - 0004 (0x30303034)
  - 0005 (0x30303035)
  - 0006 (0x30303036)
  - 0007 (0x30303037)
  - 0008 (0x30303038)
  - 0100 (0x30313030)
3. Unknown two words (or eight chars?).
