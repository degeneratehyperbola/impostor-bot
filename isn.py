from typing import Callable as Cmd

# TODO:
# Comments with # (DONE)
# Exception handling in the parsing process instead of executing process (DONE)
# Variable handling in the executing process instead of parsing process (DONE)
# Get property for any py object .......... Future me here. Das wicked niggster, hell, add a fucking eval operator (DONE)
# Call any py object's method ............. Future me here again. No words (DONE)
# Nigusi O_O (DONE)
# Detours with > or perhaps with separate command (idk, more of a frontend task)
# Scopes O_O powered by scoped_split()
# Operations on variables O_O
# Custom, human comprehensible fucking split function
# Bring back variable getter
# Variable setting from commands that return a value

### IMPOSTOR SCRIPT NOTATION ###

class VarIndexError(Exception): pass
class VarAssignError(Exception): pass
class CmdIndexError(Exception): pass
class CastError(Exception): pass

def split(text: str, delimiters: str = ' \t', quotes: str = '\"\'', comments: str = '#', escapes: str = '\\') -> list:
	buffer = []

	everything = delimiters + quotes + escapes
	for c in everything:
		if everything.count(c) > 1:
			raise ValueError('Either delimiters, quotes or escapes overlap.')

	escape_next = ''
	word = ''
	expect_quote = ''
	for c in text:
		if not escape_next:
			# Self explanatory
			if c in comments:
				break

			# Mark escaping
			if c in escapes:
				escape_next = c
				continue

			# Handle grouping
			if c == expect_quote:
				expect_quote = ''
				# Interpret empty quotes as an empty string
				if not len(word):
					buffer.append('')
				continue
			elif c in quotes and not expect_quote:
				expect_quote = c
				continue

		# Restore escape character if not used
		def needs_escaping(c):
			if c in escapes: return True
			if c == expect_quote: return True
			elif c in quotes and not expect_quote: return True

		if not needs_escaping(c):
			word += escape_next

		escape_next = ''

		# Lexical split
		if c in delimiters and len(word) and not expect_quote:
			buffer.append(word)
			word = ''
			continue
		elif not c in delimiters or expect_quote:
			word += c
			continue

	if expect_quote:
		raise SyntaxError(f'Expected closing {expect_quote}.')

	if len(word):
		buffer.append(word)

	return buffer

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
	async def setvar(self, alias: str, value: str):
		if value is None:
			raise VarAssignError(f'cannot assign VOID to "{alias}"! Variable remains unchanged.')

		self._var_reg[alias] = value

	# Parses and executes code one line at a time
	async def _interpret_line(self, line: str):
		from inspect import iscoroutinefunction as is_async
		from inspect import signature as Signature
		from inspect import Parameter
		from inspect import _empty as AnyType

		words = split(line)
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
		args_cast = args.copy()
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
						raise CastError(f'Unable to convert "{args[i]}" to type "{type_.__name__}"! Parameter {i} : "{param_name}".')
					except Exception as e:
						raise CastError(f'Internal error occured while converting arguments for command "{alias}"!\n' + str(e))
			i += 1
		
		# Execute the command
		res = None
		if is_async(fn):
			res = await fn(*args_cast)
		else:
			res = fn(*args_cast)
		
		return res

	# Splits text into a list of lines then interprets them
	async def interpret(self, text: str):
		lines = split(text, delimiters='\n', quotes='', comments='', escapes='')
		if not len(lines): return
		
		for line in lines:
			if not len(line): continue
			await self._interpret_line(line)
