from ctypes import *
import sys

__CSI = '\033['

def cur_pos(row = 1, col = 1):
	sys.stdout.write(f'{__CSI}{row};{col}H')

def clear():
	sys.stdout.write(f'{__CSI}S{__CSI}2J{__CSI}1;1H')

def echo(*args):
	sys.stdout.write(f'{__CSI}0m')
	for arg in args:
		sys.stdout.write(f'{arg} ')
	sys.stdout.write(f'{__CSI}1D {__CSI}1D\n')

def error(*args):
	sys.stdout.write(f'{__CSI}41;93m')
	for arg in args:
		sys.stdout.write(f'{arg} ')
	sys.stdout.write(f'{__CSI}0m{__CSI}1D {__CSI}1D\n')

def notice(*args):
	sys.stdout.write(f'{__CSI}44;97m')
	for arg in args:
		sys.stdout.write(f'{arg} ')
	sys.stdout.write(f'{__CSI}0m{__CSI}1D {__CSI}1D\n')

def bold(*args):
	sys.stdout.write(f'{__CSI}7m')
	for arg in args:
		sys.stdout.write(f'{arg} ')
	sys.stdout.write(f'{__CSI}0m{__CSI}1D {__CSI}1D\n')

if __name__ == 'helpers':
	windll.kernel32.SetConsoleMode(windll.kernel32.GetStdHandle(-11), 7)
