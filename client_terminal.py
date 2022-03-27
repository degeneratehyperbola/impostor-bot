from helpers import *
from typing import Callable as Cmd
from inspect import iscoroutinefunction as is_async
from asyncio import sleep
from inspect import signature as Signature
from inspect import Parameter
from inspect import _empty as AnyType
from shlex import split as posix_split
import discord

class Terminal:
	cmd_reg = {}
	var_reg = {}
	
	def register(self, alias: str, cmd: Cmd):
		self.cmd_reg[alias] = cmd
	
	#executes a command
	async def exec(self, alias: str, *args):
		fn = None
		
		# Search for a command with the given alias
		try:
			fn = self.cmd_reg[alias]
		except KeyError:
			error(f'Error: "{alias}" was not recognised as a command!')
			return
		except Exception as e:
			error(f'Unknown error occured while indexing command "{alias}"!')
			error(e)
			return
		
		res = None
		sig = Signature(fn)
		args_cast = list(args)
		i = 0
		
		# Cast all args based on the command's function signature
		for param_name in sig.parameters.keys():
			param = sig.parameters[param_name]
			type_ = param.annotation
			kind = param.kind
			
			# Keyword parameters are inaccessible
			if kind is Parameter.KEYWORD_ONLY or kind is Parameter.VAR_KEYWORD:
				continue
			
			if not type_ is AnyType:
				if kind is Parameter.VAR_POSITIONAL:
					args_var = args_cast[i:]
					
					for ii in range(len(args_var)):
						try:
							args_cast[i + ii] = type_(args_var[ii])
						except ValueError:
							error(f'Error: unable to convert "{args_var[ii]}" to type "{type_.__name__}"! Variable argument {i + ii} : "{param_name}"')
							return
						except Exception as e:
							error(f'Unknown error occured while converting variable arguments for command "{alias}"!')
							error(e)
							return
				else:
					try:
						args_cast[i] = type_(args_cast[i])
					except IndexError:
						if param.default is Parameter.empty:
							error(f'Error: missing argument "{param_name}" of type "{type_.__name__}"!')
							return
						
						break
					except ValueError:
						error(f'Error: unable to convert "{args[i]}" to type "{type_.__name__}"! Argument {i} : "{param_name}".')
						return
					except Exception as e:
						error(f'Unknown error occured while converting arguments for command "{alias}"!')
						error(e)
						return
			i += 1
		
		# Execute command
		try:
			if is_async(fn):
				res = await fn(*args_cast)
			else:
				res = fn(*args_cast)
		except TypeError:
			error('Error: too many or invalid argument(s)!')
			return
		except Exception as e:
			error(f'Unknown error occured while executing command "{alias}"!')
			error(e)
			return
		
		return res
	
	# Retrieves a variables value
	async def getvar(self, alias: str):
		val = None

		try:
			val = self.var_reg[alias]
		except KeyError:
			error(f'Error: "{alias}" was not recognised as a variable!')
			return
		except Exception as e:
			error(f'Unknown error occured while retrieving variable "{alias}"!')
			error(e)
			return
		
		return val
	
	# Assigns a value to or declares a variable
	async def setvar(self, alias: str, val):
		if val is None:
			error(f'Error: cannot assign VOID to "{alias}"! Variable remains unchanged.')
			return
		
		self.var_reg[alias] = val

	# Parses text into a command and a list of its arguments, also handles inline variables
	async def parse(self, text: str):
		# TODO:
		# - Detours with > or perhaps with separate command (idk, more of a frontend task)
		# - Scopes O_O powered by scoped_split()
		# - Operations on variables O_O
		# - Exception handling in the parsing process instead of executing process
		# - Nigusi O_O
		# - Get property for any py object .......... Future me here. Das wicked niggster, hell, add a fucking eval operator
		# - Call any py object's method ............. Future me here again. No words
		
		words = posix_split(text)
		
		if not len(words): return
		
		# No detours december
		# Try this tho VVV
		# detour = None
		# try: detour = words.index('>', 1)
		# except ValueError: pass
		# *words[(detour + 1):]
		
		alias = words[0]
		args = words[1:]
		parsed_args = list()
		
		if len(args):
			# Handle assigning and declaring vars
			if args[0] == '=':
				try:
					await self.setvar(alias, args[1])
				except IndexError:
					error(f'Error: expected a value for variable "{alias}"!')
				except Exception as e:
					error(f'Unknown error occured while setting variable "{alias}"!')
					error(e)

				return

			# Parse args
			for arg in args:
				# If an arg is marked with '@', treat as variable and get its value
				if arg.startswith('@'):
					parsed_args.append(await self.getvar(arg[1:]))
				else:
					parsed_args.append(arg)
		
		return await self.exec(alias, *parsed_args)

class Client(discord.Client):
	terminal = Terminal()
	_terminal_task = None
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._terminal_task = self.loop.create_task(self._terminal_run())
	
	async def close(self):
		error("Shutting down...")
		self._terminal_task.cancel()
		return await super().close()

	async def _terminal_run(self):
		await self.wait_until_ready()
		await sleep(0.3)
		
		while not self.is_closed():
			await self.terminal.parse(await ainput('Awesome Wallpapers > '))
	
	async def on_ready(self):
		notice('Client connected')
