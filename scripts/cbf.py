#!/usr/bin/env python3

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  version 2 as published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
cbf.py - util for checking CBF files for integrity
"""

import sys
import argparse
import struct

__author__ = "Jan Havran"

class CBF(object):
	fileData  = []
	fileTable = []

	class Header:
		size = 0x20
		sig1 = 0x46474942	# BIGF
		sig2 = 0x4C425A01	# ZBL\1
		
	def __init__(self, fileName):
		self.fileName = fileName
		self.fileData = open(fileName, "rb").read()

	def unpack(self, fmt, data):
		st_fmt = fmt
		st_len = struct.calcsize(st_fmt)
		st_unpack = struct.Struct(st_fmt).unpack_from

		return st_unpack(data[:st_len])

	def parse_header(self):
		if len(self.fileData) < CBF.Header.size:
			print(self.fileName + ": Invalid header size")
			return None

		(sig1, sig2, CBFSize, unk1, fileCnt, tableOffset, unk2, tableSize) = self.unpack("<IIIIIIII", self.fileData)

		if sig1 != CBF.Header.sig1 or sig2 != CBF.Header.sig2:
			print(self.fileName + ": Invalid header signature")
			return None
		if unk1 != 0 or unk2 != 0:
			print(self.fileName + ": Unexpected data in header")
			return None
		if len(self.fileData) != CBFSize:
			print(self.fileName + ": Invalid CBF size")
			return None
		if tableOffset + tableSize < CBFSize:
			print(self.fileName + ": Invalid file table location")
			return None

		self.fileTable = self.fileData[tableOffset:tableOffset + tableSize]

		return fileCnt

	def check(self):
		self.parse_header()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--check",
		help="check CHECK for integrity (as per reverse-engineered specification)",
		nargs="+")
	parser.add_argument("-v", "--verbose",
		help="verbose mode ON",
		action="store_true")
	args = parser.parse_args()

	if not args.check:
		parser.print_help()
		sys.exit(1)

	for fileName in args.check:
		try:
			cbr = CBF(fileName)
			cbr.check()
		except FileNotFoundError as e:
			print(e)

