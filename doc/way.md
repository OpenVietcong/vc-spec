This document describes WAY (vehicle waypoints) files.

File structure
==============

| Offset | Name | Type |
|---|---|---|
| 0 | Coordinates count | UINT32LE |
| 4 | Coordinates | Sub-blocks |

1. Identify number of coordinates sub-blocks
2. Coordinates sub-blocks following next control sub-blocks

Coordinates
-----------
Structure of each coordinates block  
Total size: 8

| Offset	| Name	| Type |
|---|---|---|
| 0	| X coord	| FLOAT32LE |
| 4	| Y coord	| FLOAT32LE |

1. 'X' vertex homogeneous coordinate
2. 'Y' vertex homogeneous coordinate

(Z coordinate is not defined because the file is only for cars and ships which collide with a terrain)
