from helpers import *
from typing import Callable as Cmd

### IMPOSTOR SCRIPT NOTATION ###

class VarIndexError(Exception): pass
class VarAssignError(Exception): pass
class CmdIndexError(Exception): pass
class CastError(Exception): pass
class ExecError(Exception): pass

class Context:
	_cmd_reg = {}
	_var_reg = {}
	
	def cmds(self):
		return self._cmd_reg.copy()
		
	def vars(self):
		return self._var_reg.copy()

	def register(self, alias: str, cmd: Cmd):
		self._cmd_reg[alias] = cmd
	
	# Retrieves a variables value
	async def getvar(self, alias: str):
		val = None

		try:
			val = self._var_reg[alias]
		except KeyError:
			raise VarIndexError(f'"{alias}" was not recognised as a variable!')
		
		return val
	
	# Assigns a value to or declares a variable
	async def setvar(self, alias: str, val: str):
		if val is None:
			raise VarAssignError(f'cannot assign VOID to "{alias}"! Variable remains unchanged.')

		self._var_reg[alias] = val

	# Parses and executes code one line at a time
	async def interpret_line(self, line: str):
		from inspect import iscoroutinefunction as is_async
		from inspect import signature as Signature
		from inspect import Parameter
		from inspect import _empty as AnyType
		from shlex import split as posix_split

		words = posix_split(line)
		if not len(words): return
		
		alias = words[0]
		args = words[1:]
		
		fn = None
		
		# Search for a command with the given alias
		try:
			fn = self._cmd_reg[alias]
		except KeyError:
			raise CmdIndexError(f'"{alias}" was not recognised as a command!')
		
		# Cast all args based on the command's function signature
		sig = Signature(fn)
		args_cast = list(args[:len(sig.parameters)])
		i = 0
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
							raise CastError(f'Unable to convert "{args_var[ii]}" to type "{type_.__name__}"! Variable argument {i + ii} : "{param_name}"')
						except Exception as e:
							raise CastError(f'Internal error occured while converting variable arguments for command "{alias}"!\n' + str(e))
				else:
					try:
						args_cast[i] = type_(args_cast[i])
					except IndexError:
						if param.default is Parameter.empty:
							raise CastError(f'Missing argument "{param_name}" of type "{type_.__name__}"!')
						break
					except ValueError:
						raise CastError(f'Unable to convert "{args[i]}" to type "{type_.__name__}"! Argument {i} : "{param_name}".')
					except Exception as e:
						raise CastError(f'Internal error occured while converting arguments for command "{alias}"!\n' + str(e))
			i += 1
		
		# Execute the command
		res = None
		try:
			if is_async(fn):
				res = await fn(*args_cast)
			else:
				res = fn(*args_cast)
		except Exception as e:
			raise ExecError(f'Internal error occured while executing command "{alias}"!\n' + str(e))
		
		return res

	# Parses text into a list of lines then interprets them
	async def parse(self, text: str):
		# TODO:
		# - Comments with #
		# - Detours with > or perhaps with separate command (idk, more of a frontend task)
		# - Scopes O_O powered by scoped_split()
		# - Operations on variables O_O
		# - Exception handling in the parsing process instead of executing process
		# - Variable handling in the executing process instead of parsing process
		# - Nigusi O_O
		# - Get property for any py object .......... Future me here. Das wicked niggster, hell, add a fucking eval operator
		# - Call any py object's method ............. Future me here again. No words
		
		lines = text.split('\n')
		if not len(lines): return
		
		for line in lines:
			# Strip a line of its comments
			line_stripped = line
			try:
				line_stripped = line[:line.index('#')]
			except:
				pass

			if not len(line_stripped): continue

			await self.interpret_line(line_stripped)
