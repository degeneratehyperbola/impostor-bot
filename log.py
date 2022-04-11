from sys import stdout

__ESC = '\033'
__CSI = f'{__ESC}['

def cur_pos(row: int = 1, col: int = 1):
	stdout.write(f'{__CSI}{row};{col}H')

def clear_line():
	stdout.write(f'{__CSI}2K{__CSI}G')

def clear(scroll: bool = False):
	stdout.write(f'{__CSI}2J')
	if scroll:
		stdout.write(f'{__CSI}3J')
	stdout.write(f'{__CSI}1;1H')

def echo(*args: str, sep: str = ' ', end: str = '\n'):
	stdout.write(f'{__CSI}90m')
	stdout.write(sep.join([str(i) for i in args]))
	stdout.write(f'{__CSI}0m{end}')

def bold(*args: str, sep: str = ' ', end: str = '\n'):
	stdout.write(f'{__CSI}97m')
	stdout.write(sep.join([str(i) for i in args]))
	stdout.write(f'{__CSI}0m{end}')

def error(*args: str, sep: str = ' ', end: str = '\n'):
	stdout.write(f'{__CSI}91m')
	stdout.write(sep.join([str(i) for i in args]))
	stdout.write(f'{__CSI}0m{end}')

# def color(r: int = 255, g: int = 255, b: int = 255):
# 	stdout.write(f'{__CSI}38;2;{r};{g},{b}m')

if __name__ == 'log':
	from sys import platform
	match platform:
		case 'win32':
			from ctypes import windll
			windll.kernel32.SetConsoleMode(windll.kernel32.GetStdHandle(-11), 7)
