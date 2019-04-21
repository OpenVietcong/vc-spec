
This document describes CTR (control) files.

This file is made of:
* Header
* Controls
* Inventory

Header
======

Total size: 8

| Offset | Name | Type |
|---|---|---|
| 0 | Signature | CHAR[4] |
| 4 | Unknown | UINT32LE |

1. Identify the CTR file, contains fixed string 'SRTC' (0x53 0x52 0x54 0x43)
2. Unknown - always 0x0C


Controls
========

Every control is always defined by two keys (primary and secondary), except from last null block and exceptions. Controls block ends with null block (control block filled with null characters).

| Offset	| Name	| Type |
|---|---|---|
| 0	| Count	| UINT32LE |
| 4	| Control	| Sub-blocks |
| ...	| Null	| NULL |

1. Identify number of control sub-blocks (including last null block), in Vietcong 1.60 files is equal to 60
2. Control sub-blocks following next control sub-blocks
3. Last control sub-block filled with null characters

Control
-------

Structure of each control  
Total size: 24

| Offset | Name | Type |
|---|---|---|
| 0 | Index | UINT32LE |
| 4 | Primary key | Sub-block |
| 12 | Secondary key | Sub-block |
| 20 | Null | NULL[4] |

1. Specifies the control
2. Primary key sub-block
3. Secondary key sub-block
4. Space filled with null characters


Exceptions
----------

Inside some control blocks are stored other setting elements.

| Index	| Offset |	Size |	Name | Type |
|---|---|---|---|---|
| 0x28 |	20 |	1 |	Reverse mouse |	UINT32 |
| 0x29 |	20 |	1 |	Mouse look |	UINT32 |
| 0x2A |	20 |	4 |	Mouse sensitivity |	FLOAT32LE |
| 0x2B |	20 |	4 |	Keyboard turn speed |	FLOAT32LE |

1-2. Boolean value (0 - unchecked, 1 - checked)  
3-4. Value between 0 - 1

### Keys

Structure of each key  
Total size: 8

| Offset |	Name |	Type |
|---|---|---|
|0 |	Device |	UINT32LE |
|4 |	Key |	UINT32LE |

1. Identify the device which the key belongs to:
*	Keyboard (0x01)
*	Mouse (0x02)
*	Undefined (0x00)
2. This table shows how the keys are represented:

**a)	For keyboard**

 
| Key |	Label |
|---|---|
| Esc |	0x01 |
| 1 |	0x02 |
| 2 |	0x03 |
| 3 |	0x04 |
| 4 |	0x05 |
| 5 |	0x06 |
| 6 |	0x07 |
| 7 |	0x08 |
| 8 |	0x09 |
| 9 |	0x0A |
| 0 |	0x0B |
| - |	0x0C |
| = |	0x0D |
| Backspace |	0x0E |
| Tab |	0x0F |
| Q |	0x10 |
| W |	0x11 |
| E |	0x12 |
| R |	0x13 |
| T |	0x14 |
| Y |	0x15 |
| U |	0x16 |
| I |	0x17 |
| O |	0x18 |
| P |	0x19 |
| [ |	0x1A |
| ] |	0x1B |
| Enter |	0x1C |
| Left Ctrl |	0x1D |
| A |	0x1E |
| S |	0x1F |
| D |	0x20 |
| F |	0x21 |
| G |	0x22 |
| H |	0x23 |
| J |	0x24 |
| K |	0x25 |
| L |	0x26 |
| ; |	0x27 |
| ' |	0x28 |
| ~ |	0x29 |
| Left Shift |	0x2A |
| \ |	0x2B |
| Z |	0x2C |
| X |	0x2D |
| C |	0x2E |
| V |	0x2F |
| B |	0x30 |
| N |	0x31 |
| M |	0x32 |
| , |	0x33 |
| . |	0x34 |
| / |	0x35 |
| Right Shift |	0x36 |
| Num * |	0x37 |
| Left Alt |	0x38 |
| Space |	0x39 |
| Caps Lock |	0x3A |
| F1 |	0x3B |
| F2 |	0x3C |
| F3 |	0x3D |
| F4 |	0x3E |
| F5 |	0x3F |
| F6 |	0x40 |
| F7 |	0x41 |
| F8 |	0x42 |
| F9 |	0x43 |
| F10 |	0x44 |
| Num Lock |	0x45 |
| Scroll Lock |	0x46 |
| Num 7 |	0x47 |
| Num 8 |	0x48 |
| Num 9 |	0x49 |
| Num - |	0x4A |
| Num 4 |	0x4B |
| Num 5 |	0x4C |
| Num 6 |	0x4D |
| Num + |	0x4E |
| Num 1 |	0x4F |
| Num 2 |	0x50 |
| Num 3 |	0x51 |
| Num 0 |	0x52 |
| Num . |	0x53 |
| F11 |	0x57 |
| F12 |	0x58 |
| Right Ctrl |	0x9D |
| Num / |	0xB5 |
| Prnt Scrn |	0xB7 |
| Pause |	0xC5 |
| Home |	0xC7 |
| Cursor Up |	0xC8 |
| Page Up |	0xC9 |
| Cursor Left |	0xCB |
| Cursor Right |	0xCD |
| End |	0xCF |
| Cursor Down |	0xD0 |
| Page Down |	0xD1 |
| Insert |	0xD2 |
| Delete |	0xD3 |
| Windows L |	0xDB |
| Windows R |	0xDC |
| Menu | 0xDD |
| Napájení |	0xDE |

**b)	For mouse**

| Key |	Label |
|---|---|
| Mouse O - |	0x01 |
| Mouse O + |	0x02 |
| Mouse wheel+ | 0x04 |
| Mouse wheel- |	0x05 |
| Left Mouse Button |	0x0A |
| Right Mouse Button |	0x0B |
| Middle Mouse Button |	0x0C |
| Mouse T |	0x0D |

**c)	Undefined**

Always 0x00


### Controls by index

This table shows which control is linked to each index.


| Control |	Index |
|---|---|
| Forward |	0x01 |
| Backward |	0x02 |
| Strafe Left |	0x03 |
| Strafe Right |	0x04 |
| Turn Left |	0x05 |
| Turn Right |	0x06 |
| Look Up |	0x07 |
| Look Down |	0x08 |
| Center View |	0x09 |
| Jump |	0x0A |
| Crouch |	0x0B |
| Lie |	0x0C |
| Lean Left |	0x0D |
| Lean Right |	0x0E |
| Walk | 0x0F |
| Shoot |	0x10 |
| Aim |	0x11 |
| Reload |	0x12 |
| Change fire rate |	0x13 |
| Use |	0x14 |
| Drop |	0x15 |
| Command menu |	0x16 |
| Info |	0x17 |
| Select side |	0x18 |
| Knife |	0x19 |
| Pistol |	0x1A |
| Main weapon |	0x1B |
| Equipment |	0x1C |
| US Grenade |	0x1D |
| VC Grenade |	0x1E |
| Lightstick |	0x1F |
| Medkit |	0x20 |
| Call Pointman |	0x21 |
| Call Medic |	0x22 |
| Call Engineer |	0x23 |
| Call Radioman |	0x24 |
| Call Machinegunner |	0x25 |
| Turbo [[1]](#notes)|	0x26 |
| Jet Pack [[2]](#notes)|	0x27 |
| [EXCEPTION](#exceptions) |	0x28 |
| [EXCEPTION](#exceptions) |	0x29 |
| [EXCEPTION](#exceptions) |	0x2A |
| [EXCEPTION](#exceptions) |	0x2B |
| Commence voice-chat |	0x2C |
| Trapkit |	0x2D |
| Map |	0x2E |
| Prev Weapon |	0x2F |
| Next Weapon |	0x30 |
| Show Intel |	0x31 |
| Flash light |	0x32 |
| Quick Save |	0x33 |
| Quick Load |	0x34 |
| Binoculars |	0x35 |
| Inventory [[3]](#notes)|0x36 |
| Select class |	0x37 |
| Chat all |	0x38 |
| Chat team |	0x39 |
| Last used weapon |	0x3A |
| Bayonet |	0x3B |

Inventory
=========
Contains information about inventory order.
This block is missing in Vietcong demo versions under v0.98.

Total size: variable

| Offset |	Name |	Type |
|---|---|---|
| 0 |	Label |	CHAR[4] |
| 4 |	Unknown |	UINT32LE |
| 8 |	Unknown |	UINT32LE |
| 12 |	Item count |	UINT32LE |

1. Label of this sub-block - always 0x63666878 'cfhx'
2. Unknown - always 0x10
3. Unknown - always 0x01
4. Identify number of items and the inventory order

* Default (0x00), the inventory order is default, size of this block is 16
* Item count (1-10), applies if the inventory order was changed (zero count cannot be reached, it is equal to default), every item adds 4 to size, so the maximum block size could reach 56

| Offset |	Name |	Type |
|---|---|---|
| 16 |	1st Position |	UINT32LE |
| 20 |	2nd Position |	UINT32LE |
| 24 |	3rd Position |	UINT32LE |
| 28 |	4th Position |	UINT32LE |
| 32 |	5th Position |	UINT32LE |
| 36 |	6th Position |	UINT32LE |
| 40 |	7th Position |	UINT32LE |
| 44 |	8th Position |	UINT32LE |
| 48 |	9th Position |	UINT32LE |
| 52 |	10th Position |	UINT32LE |

1-10. Specifies which item is in its position

**List of items:**

| Item |	Label |
|---|---|
| Knife |	0x00 |
| Pistol |	0x01 |
| Main weapon |	0x02 |
| Equipment |	0x03 |
| Grenades |	0x04 |
| Vietcong grenades |	0x05 |
| Medikit |	0x06 |
| Lightsticks |	0x07 |
| Map |	0x08 |
| Booby-Trap |	0x09 |

### Notes
[1] Available only in Vietcong editor v1.35 or v1.61  
[2] Available only in Vietcong editor v1.35 or v1.61  
[3] Inventory control has been removed in Vietcong demo v0.98
