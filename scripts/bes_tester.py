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
bes_tester.py - util for checking BES files for integrity
"""

import sys
import argparse
import os
import struct
import logging

__author__ = "Jan Havran"

logging.VERBOSE = logging.DEBUG + 5

def hex_dump(data, index):
	for i in range(len(data)):
		if i % 16 == 0:
			sys.stdout.write("{}{:04x}:".format(" "*(index*2), i))
		sys.stdout.write(" {:02x}".format(data[i]))
		if i % 16 == 15:
			print()
	print()

def pchar_to_string(pchar):
	return str(pchar, 'ascii').strip(chr(0))

class BES(object):
	vertices = []
	faces = []
	def __init__(self, fname):
		self.f = open(fname, "rb")

		self.vertices = [(0, 0, 0), (5, 0, 0), (2.5, 5, 0)]
		self.faces = [(0, 1, 2)]

		self.vertices = []
		self.faces = []
		self.read_header()
		self.read_preview()
		self.read_data()

	def unpack(self, fmt, data):
		st_fmt = fmt
		st_len = struct.calcsize(st_fmt)
		st_unpack = struct.Struct(st_fmt).unpack_from
		return st_unpack(data[:st_len])

	def read_header(self):
		data = self.f.read(0x10)
		print(self.unpack("<5s4sI3c", data))

	def read_preview(self):
		self.f.read(0x3000)

	def read_data(self):
		data = self.f.read()
		self.parse_data(data, 0)

	def parse_data(self, data, index):
		start = 0
		while (len(data[start:]) > 8):
			(label, size) = self.unpack("<II", data[start:])
			subblock = data[start+8:start+size]
			start += size

			if   label == 0x0001:
				self.parse_block_object(subblock, index)
			elif label == 0x0030:
				self.parse_block_unk30(subblock, index)
			elif label == 0x0031:
				self.parse_block_mesh(subblock, index)
			elif label == 0x0032:
				self.parse_block_vertices(subblock, index)
			elif label == 0x0033:
				self.parse_block_faces(subblock, index)
			elif label == 0x0034:
				self.parse_block_properties(subblock, index)
			elif label == 0x0035:
				self.parse_block_unk35(subblock, index)
			elif label == 0x0036:
				self.parse_block_unk36(subblock, index)
			elif label == 0x0038:
				self.parse_block_unk38(subblock, index)
			elif label == 0x0070:
				self.parse_block_user_info(subblock, index)
			elif label == 0x1000:
				self.parse_block_material(subblock, index)
			elif label == 0x1001:
				self.parse_block_bitmap(subblock, index)
			elif label == 0x1002:
				self.parse_block_ptero_mat(subblock, index)
			else:
				logging.warning("Unknown block {}".format(hex(label)))
				hex_dump(subblock, index)

	def parse_block_object(self, data, index):
		(children, name_size) = self.unpack("<II", data)
		(name,) = self.unpack("<" + str(name_size) + "s", data[8:])
		logging.log(logging.VERBOSE, "{}Object ({} B) - children: {}, name({}): {}".format(
			" "*(index*2), len(data), children, name_size,	pchar_to_string(name)))

		self.parse_data(data[8+name_size:], index + 1)

	def parse_block_unk30(self, data, index):
		(children,) = self.unpack("<I", data)
		logging.log(logging.VERBOSE, "{}Unk30 ({} B) - Number of meshes: {:08x}".format(
			" "*(index*2), len(data), children))

		self.parse_data(data[4:], index + 1)

	def parse_block_mesh(self, data, index):
		(material,) = self.unpack("<I", data)
		logging.log(logging.VERBOSE, "{}Mesh ({} B) - Material: {:08x}".format(
			" "*(index*2), len(data), material))

		self.parse_data(data[4:], index + 1)

	def parse_block_vertices(self, data, index):
		(count, size, unknown) = self.unpack("<III", data)

		logging.log(logging.VERBOSE, "{}Vertices ({} B) - count: {}, size: {}, unknown: {:08x}".format(
			" "*(index*2), len(data), count, size, unknown))

		if size < 12:
			logging.error("Unsupported size '{}' of vertex struct".format(size))
		if len(data[12:]) != size * count:
			logging.error("Block size do not match")

	def parse_block_faces(self, data, index):
		(count, ) = self.unpack("<I", data)

		logging.log(logging.VERBOSE, "{}Faces ({} B) - count: {}".format(
			" "*(index*2), len(data), count))

		if len(data[4:]) != count * 12:
			logging.error("Block size do not match")

	def parse_block_properties(self, data, index):
		(count, ) = self.unpack("<I", data)
		(prop,) = self.unpack("<" + str(count) + "s", data[4:])
		logging.log(logging.VERBOSE, "{}Properties ({} B): {}".format(
			" "*(index*2), len(data), pchar_to_string(prop)))

		if count + 4 != len(data):
			logging.error("Block size do not match: {} vs {}".format(len(data), count))

	def parse_block_unk35(self, data, index):
		(x, y, z) = self.unpack("<fff", data)
		logging.log(logging.VERBOSE, "{}Unk35 ({} B) - position: [{}][{}][{}]".format(
			" "*(index*2), len(data), x, y, z))

	def parse_block_unk36(self, data, index):
		logging.log(logging.VERBOSE, "{}Unk36 ({} B)".format(
			" "*(index*2), len(data)))

	def parse_block_unk38(self, data, index):
		logging.log(logging.VERBOSE, "{}Unk38 ({} B)".format(
			" "*(index*2), len(data)))

	def parse_block_user_info(self, data, index):
		(name_size, comment_size, unknown) = self.unpack("<III", data)
		(name,) = self.unpack("<" + str(name_size) + "s", data[12:])
		(comment,) = self.unpack("<" + str(comment_size) + "s", data[76:])
		logging.log(logging.VERBOSE,
			"{}User info ({} B) - name({}): {}, comment({}): {}, unknown: {:08x}".format(
				" "*(index*2), len(data), name_size, pchar_to_string(name),
				comment_size, pchar_to_string(comment), unknown))

	def parse_block_material(self, data, index):
		(children,) = self.unpack("<I", data)
		logging.log(logging.VERBOSE, "{}Material ({} B) - Number of materials: {:08x}".format(
			" "*(index*2), len(data), children))

		self.parse_data(data[4:], index + 1)

	def parse_block_bitmap(self, data, index):
		(unk1, unk2, unk3, name_size, unk4) = self.unpack("<IIIII", data)
		(name,) = self.unpack("<" + str(name_size) + "s", data[20:])
		logging.log(logging.VERBOSE, "{}Bitmap ({} B) - name({}): {}".format(
			" "*(index*2), len(data), name_size, pchar_to_string(name)))

	def parse_block_ptero_mat(self, data, index):
		(unk1, unk2, unk3, unk4, unk5) = self.unpack("<II4sI4s", data)
		(name_size,) = self.unpack("<I", data[20:])
		(name,) = self.unpack("<" + str(name_size) + "s", data[24:])
		logging.log(logging.VERBOSE,
			"{}PteroMat ({} B) - name({}): {}, collision material: '{}{}', grow type: '{}', grass type: '{}'".format(
			" "*(index*2), len(data), name_size, pchar_to_string(name), chr(unk3[0]),
			chr(unk3[1]), chr(unk5[0]), chr(unk5[1])))

if __name__ == "__main__":
	level = logging.INFO

	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--check",
		help="check CHECK for integrity (as per reverse-engineered specification)",
		nargs="?")
	parser.add_argument("-v", "--verbose",
		help="verbose mode ON",
		action="store_true")
	args = parser.parse_args()

	if args.verbose:
		level = logging.VERBOSE

	logging.basicConfig(level=level, format="%(message)s")

	if args.check:
		logging.info("Model: " + args.check)
		BES(args.check)
	else:
		parser.print_help()
		sys.exit(1)

