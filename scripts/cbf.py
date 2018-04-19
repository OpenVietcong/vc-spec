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
cbf.py - util for unpacking (not compressed) CBF files and checking them for integrity
"""

import sys
import argparse
import struct
import os

__author__ = "Jan Havran"

class CBF(object):
	fileData  = []
	fileTable = []
	fileList  = []

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

	def decryptTableItem(self, encryptedItem):
		lookUpTable = [0x32, 0xF3, 0x1E, 0x06, 0x45, 0x70, 0x32, 0xAA, 0x55, 0x3F, 0xF1, 0xDE, 0xA3, 0x44, 0x21, 0xB4]
		itemLength = len(encryptedItem)
		decryptedItem = bytearray(itemLength)

		key = itemLength
		for pos in range(itemLength):
			encryptedByte = encryptedItem[pos]
			decryptedByte = encryptedByte ^ lookUpTable[key & 0xF]
			key = encryptedByte
			decryptedItem[pos] = decryptedByte

		return bytes(decryptedItem)

	def decryptFile(self, encryptedFile):
		fileLength = len(encryptedFile)
		decryptedFile = bytearray(fileLength)

		key = fileLength & 0xFF
		for pos in range(fileLength):
			encryptedByte = encryptedFile[pos]
			decryptedByte = ((encryptedByte + 0xA6 + key) & 0xFF) ^ key
			decryptedFile[pos] = decryptedByte

		return bytes(decryptedFile)

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

	def parse_table(self):
		pos = 0

		while pos < len(self.fileTable):
			if pos + 2 > len(self.fileTable):
				print(self.fileName + ": Corrupted item size in file table")
				return
			(itemSize, ) = self.unpack("<H", self.fileTable[pos:])
			pos += 2

			if pos + itemSize > len(self.fileTable):
				print(self.fileName + ": Corrupted item in file table")
				return
			itemData = self.decryptTableItem(self.fileTable[pos:pos+itemSize])
			pos += itemSize

			(fileOffset, unk1, unk2, unk3, unk4) = self.unpack("<I4I", itemData)
			(fileSize, unk5, unk6, fileCompress, unk7) = self.unpack("<I2II1I", itemData[20:])

			(fileName, ) = self.unpack("<" + str(itemSize - 40) + "s", itemData[40:])
			if fileName[-1] != 0x0:
				print(self.fileName + ": Corrupted item name in file table")
				return
			fileName = str(fileName, 'windows-1250').strip(chr(0))

			self.fileList.append((fileName, self.fileData[fileOffset:fileOffset + fileSize], fileCompress))
		return None

	def parse_file(self, file):
		parsed_file = bytes(0)
		if not file[2]:
			parsed_file = self.decryptFile(file[1])

		return parsed_file

	def parse_files(self):
		for file in self.fileList:
			fileName = file[0].replace("\\", "/")
			if not os.path.exists(os.path.dirname(fileName)):
				os.makedirs(os.path.dirname(fileName))

			fileData = self.parse_file(file)
			fileWrite = open(fileName, "wb")
			fileWrite.write(fileData)
			fileWrite.close()

	def check(self):
		self.parse_header()
		self.parse_table()

	def extract(self):
		self.parse_header()
		self.parse_table()
		self.parse_files()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--check",
		help="check CHECK for integrity (as per reverse-engineered specification)",
		nargs="+")
	parser.add_argument("-x", "--extract",
		help="extract files from an EXTRACT archive",
		nargs="?")
	parser.add_argument("-v", "--verbose",
		help="verbose mode ON",
		action="store_true")
	args = parser.parse_args()

	if not (args.check or args.extract):
		parser.print_help()
		sys.exit(1)

	if args.check:
		for fileName in args.check:
			try:
				cbr = CBF(fileName)
				cbr.check()
			except FileNotFoundError as e:
				print(e)

	if args.extract:
		cbf = CBF(args.extract)
		cbf.extract()

