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
cbf.py - util for unpacking CBF files and checking them for integrity
"""

import sys
import argparse
import struct
import os
import ntpath
import logging

__author__ = "Jan Havran"

logging.VERBOSE = logging.DEBUG + 5

class LZW(object):
    class Header:
        sig = b'[..]'

    class Default:
        ptrRoot = 0xFFFFFFFF
        dictWidth = 8

    def __init__(self, data):
        self.LZWDict = []
        self.data = data
        self.dictWidth = LZW.Default.dictWidth
        self.codeEnd = (1 << self.dictWidth)
        self.codeMax = (1 << self.dictWidth) - 1
        self.dataPos = 0

        logging.debug("Initializing LZW dictionary")
        for row in range(self.codeEnd):
            self.appendRow(LZW.Default.ptrRoot, row)
        self.appendRow(LZW.Default.ptrRoot, self.codeEnd)

    def getDictRowLen(self, key):
        len = 1

        while self.LZWDict[key][0] != LZW.Default.ptrRoot:
            key = self.LZWDict[key][0]
            len += 1

        return len

    def appendRow(self, ptr, val):
        self.LZWDict.append((ptr, val))

        if len(self.LZWDict) >= self.codeMax:
            self.dictWidth += 1
            self.codeMax = (1 << self.dictWidth) - 1
            logging.debug("Dictionary key width extended to {} bits".format(self.dictWidth))
            if self.dictWidth == 33:
                logging.error("LZW key width exceeded 32 bits")

    def getKeyFromStream(self):
        dataPosB = self.dataPos // 8
        b0 = self.data[dataPosB + 0] & 0xFF
        b1 = 0x00 if dataPosB + 1 >=  len(self.data) else self.data[dataPosB + 1] & 0xFF
        b2 = 0x00 if dataPosB + 2 >=  len(self.data) else self.data[dataPosB + 2] & 0xFF
        b3 = 0x00 if dataPosB + 3 >=  len(self.data) else self.data[dataPosB + 3] & 0xFF

        word = (b0 << 0) | (b1 << 8) | (b2 << 16) | (b3 << 24)
        key = word >> (self.dataPos % 8)
        key = key & self.codeMax

        self.dataPos += self.dictWidth

        return key

    def getValFromDict(self, key, index):
        len = self.getDictRowLen(key)

        pos = 0
        while pos < len - index:
            val = self.LZWDict[key][1]
            key = self.LZWDict[key][0]
            pos += 1

        return val

    def decompress(self):
        data = bytearray(0)
        keyPrev = LZW.Default.ptrRoot

        keyCurr = self.getKeyFromStream()
        while keyCurr != self.codeEnd:
            if keyPrev != LZW.Default.ptrRoot:
                if keyCurr < len(self.LZWDict):
                    val = self.getValFromDict(keyCurr, 0)
                elif keyCurr == len(self.LZWDict):
                    val = self.getValFromDict(keyPrev, 0)
                else:
                    raise RuntimeError("    LZW: invalid key")

                self.appendRow(keyPrev, val)

            for index in range(self.getDictRowLen(keyCurr)):
                data.append(self.getValFromDict(keyCurr, index))

            keyPrev = keyCurr
            keyCurr = self.getKeyFromStream()

        return bytes(data)

class CBFFile(object):
    def __init__(self, version, name, size, data, compressed):
        self.version = version
        self.basename = ntpath.basename(name)
        self.dirname  = ntpath.dirname(name).split("\\")
        self.size = size
        self.data = data
        self.compressed = compressed

    def decompress(self):
        dataPtr = 0
        fileDecompressed = bytearray(0)

        while dataPtr + 12 < len(self.data):
            (sig, blockCompressedSize, blockDecompressedSize) = unpack("<4sII", self.data[dataPtr:])
            dataPtr += 12

            if sig != LZW.Header.sig:
                raise RuntimeError("    LZW: Invalid header signature")

            if len(self.data[dataPtr:]) < blockCompressedSize:
                raise RuntimeError("    LZW: not enough data in LZW block")

            blockCompressed = self.data[dataPtr:dataPtr+blockCompressedSize]
            lzw = LZW(blockCompressed)
            blockDecompressed = lzw.decompress()

            if len(blockDecompressed) != blockDecompressedSize:
                logging.error("    LZW: Invalid size of decompressed LZW block")

            fileDecompressed += blockDecompressed
            dataPtr += blockCompressedSize

        if dataPtr != len(self.data):
            logging.error("    LZW: invalid size of compressed file")

        return bytes(fileDecompressed)

    def decrypt(self):
        encryptedFile = self.data
        fileLength = len(encryptedFile)
        decryptedFile = bytearray(fileLength)

        key = fileLength & 0xFF
        for pos in range(fileLength):
            encryptedByte = encryptedFile[pos]
            decryptedByte = ((encryptedByte + 0xA6 + key) & 0xFF) ^ key
            decryptedFile[pos] = decryptedByte

        return bytes(decryptedFile)

    def extractData(self):
        extractedData = bytes()

        if   self.compressed == 0 and self.version == CBFArchive.Version.ZBL0:
            logging.log(logging.VERBOSE, "  extracting: " + self.basename)
            extractedData = self.data
        elif self.compressed == 0 and self.version == CBFArchive.Version.ZBL1:
            logging.log(logging.VERBOSE, "  decrypting: " + self.basename)
            extractedData = self.decrypt()
        elif self.compressed == 1:
            logging.log(logging.VERBOSE, "  inflating: " + self.basename)
            extractedData = self.decompress()
        else:
            logging.error("    Skipping (Unknown compression method): " + self.basename)

        if self.size != len(extractedData):
            logging.error("    Invalid size of extracted file")

        return extractedData

class CBFArchive(object):
    class Header:
        size = 0x34
        sig = b'BIGF'

    class Version:
        ZBL0 = b'\x00ZBL'
        ZBL1 = b'\x01ZBL'

    class Mode:
        classic = 0
        extended = 1

    class Table:
        itemSize = 0x28

    def __init__(self, name, data):
        self.fileVer  = CBFArchive.Version.ZBL0
        self.fileMode = CBFArchive.Mode.classic
        self.fileName = name
        self.fileData = data

    def decrypt(self, encryptedItem):
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

    def parse_header(self):
        if len(self.fileData) < CBFArchive.Header.size:
            raise RuntimeError("  Invalid header size")

        (sig, ver, CBFSize, res1, fileCnt, tableOffset, res2, tableSize, res3) = unpack("<4s4sIIIIIII", self.fileData)
        (headerSize, res4, lowDateTime, highDateTime) = unpack("<IIII", self.fileData[36:])

        if sig != CBFArchive.Header.sig:
            raise RuntimeError("  Invalid header signature")

        if ver == CBFArchive.Version.ZBL0:
            self.fileVer = CBFArchive.Version.ZBL0
        elif ver == CBFArchive.Version.ZBL1:
            self.fileVer = CBFArchive.Version.ZBL1
        else:
            raise RuntimeError("  Unknown CBF version")

        if tableOffset + tableSize > CBFSize:
            raise RuntimeError("  Invalid file table location")
        if tableOffset + tableSize < CBFSize:
            logging.warning("  Unknown data after file table")

        if len(self.fileData) != CBFSize:
            logging.error("  Invalid CBF size")
        if res1 != 0 or res2 != 0 or res3 != 0 or res4 != 0:
            logging.warning("  Non-zero reserved data in header")

        if ver == CBFArchive.Version.ZBL0 and headerSize != 64:
            raise RuntimeError("  Invalid header size for ZBL0 version")

        if headerSize != 0:
            if len(self.fileData) < headerSize:
                raise RuntimeError("  Invalid header size with extensions")

            if headerSize >= 64:
                res5 = unpack("<III", self.fileData[52:])
                if res5[0] != 0 or res5[1] != 0 or res5[2] != 0:
                    logging.warning("  Non-zero reserved data in externsion header")

                if headerSize >= 70:
                    (label, commentSize) = unpack("<HI", self.fileData[64:])
                    (comment,) = unpack("<" + str(commentSize) + "s", self.fileData[70:])
                    comment = str(comment, 'windows-1250')
                    logging.debug("Comment: " + comment)
                elif headerSize > 64:
                    logging.warning("  Invalid extension header size")
            else:
                logging.warning("  Invalid extension header size")

        self.fileMode = CBFArchive.Mode.extended if headerSize > 0 else CBFArchive.Mode.classic

        return (fileCnt, self.fileData[tableOffset:tableOffset + tableSize])

    def parse_table(self, fileTable):
        fileList = []
        pos = 0
        itemSize = CBFArchive.Table.itemSize
        descSize = 0 if self.fileVer == CBFArchive.Version.ZBL0 else 2

        while pos < len(fileTable):
            if pos + descSize > len(fileTable):
                logging.error("  Corrupted item size in file table")
                break

            if self.fileVer == CBFArchive.Version.ZBL1:
                (itemSize, ) = unpack("<H",fileTable[pos:])
                pos += descSize

            """
            Table item must be in the bounds of Table of Files and also must be at least as big as
            table item plus two (empty file name and file name of zero length is forbidden)
            """
            if (pos + itemSize > len(fileTable)) or (itemSize < CBFArchive.Table.itemSize):
                logging.error("  Corrupted item in file table")
                break

            itemData = fileTable[pos:pos+itemSize]
            if self.fileVer == CBFArchive.Version.ZBL1:
                itemData = self.decrypt(itemData)
            pos += itemSize

            (fileOffset, res1, unk1, lowDateTime, highDateTime) = unpack("<I4I", itemData)
            (fileSize, res2, fileCompressedSize, fileStorageType, unk2) = unpack("<IIIII", itemData[20:])

            if res1 != 0 or res2 != 0:
                logging.warning("  Non-zero reserved data in file desc")

            if self.fileMode == CBFArchive.Mode.classic:
                if unk1 != 0 or lowDateTime != 0 or highDateTime != 0:
                    logging.warning("  Non-zero reserved data in classic file desc")
            #else:
            #    date = lowDateTime + (highDateTime)...

            if self.fileVer == CBFArchive.Version.ZBL0:
                null_pos = fileTable[pos:].find(b'\x00')
                if null_pos == -1:
                    logging.error("  Corrupted item name in file table")
                    break
                fileName = fileTable[pos:pos+null_pos + 1]
                pos += null_pos + 1
            else:
                (fileName, ) = unpack("<" + str(itemSize - CBFArchive.Table.itemSize) + "s", itemData[CBFArchive.Table.itemSize:])
                if fileName[-1] != 0x0:
                    logging.error("  Corrupted item name in file table")
                    break

            fileName = str(fileName, 'windows-1250').strip(chr(0))

            if fileStorageType == 0:
                fileStoredSize = fileSize
                if fileCompressedSize != 0:
                    logging.warning("  Compressed size should be zero for non-compressed files")
            elif fileStorageType == 1:
                fileStoredSize = fileCompressedSize
            else:
                logging.error("  Unknown storage type: " + hex(fileStorageType))
                continue

            if fileOffset + fileStoredSize > len(self.fileData):
                logging.error("  Invalid file data location")
                continue

            file = CBFFile(self.fileVer, fileName, fileSize, self.fileData[fileOffset:fileOffset + fileStoredSize], fileStorageType)
            fileList.append(file)

        return fileList

    def parse_files(self, fileList, extract):
        for file in fileList:
            if extract:
                fileDir = os.path.join(*file.dirname)
                filePath = os.path.join(fileDir, file.basename)

                if fileDir and not os.path.exists(fileDir):
                    os.makedirs(fileDir)

            fileData = file.extractData()
            if extract:
                fileWrite = open(filePath, "wb")
                fileWrite.write(fileData)
                fileWrite.close()
                os.utime(filePath, (0, 0))

    def parse(self, extract):
        (fileCnt, fileTable) = self.parse_header()
        fileList = self.parse_table(fileTable)
        if len(fileList) != fileCnt:
            logging.error("Found {} files, but CBF should contain {} files".format(len(fileList), fileCnt))
        self.parse_files(fileList, extract)

def unpack(fmt, data):
        st_fmt = fmt
        st_len = struct.calcsize(st_fmt)
        st_unpack = struct.Struct(st_fmt).unpack_from

        return st_unpack(data[:st_len])

def processFile(fileName, extract):
    logging.info("Archive: " + fileName)
    try:
        data = open(fileName, "rb").read()
        cbf = CBFArchive(fileName, data)
        cbf.parse(extract)
    except FileNotFoundError as e:
        logging.error(e)
    except RuntimeError as e:
        logging.error(e)

if __name__ == "__main__":
    level = logging.INFO

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


    if args.verbose:
        level = logging.VERBOSE

    logging.basicConfig(level=level, format="%(message)s")

    if not (args.check or args.extract):
        parser.print_help()
        sys.exit(1)

    if args.check:
        for fileName in args.check:
            processFile(fileName, False)

    if args.extract:
        processFile(args.extract, True)

