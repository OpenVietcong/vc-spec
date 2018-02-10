#!/usr/bin/env python3

import sys
import argparse
from PIL import Image

def help():
	print("bes_preview.py <BES_FILE>")

if len(sys.argv) != 2:
	help()
	sys.exit()

data = open(sys.argv[1], 'rb').read()

img = Image.new('RGB', (64, 64), 'white')

for row in range(0, 64):
	for col in range(0, 64):
		b = data[16+row*192+col*3+0]
		g = data[16+row*192+col*3+1]
		r = data[16+row*192+col*3+2]
		img.putpixel((col, row), (r, g, b))

img.save(sys.argv[1] + ".png", 'PNG')
