from typing import Callable

### IMPOSTOR SCRIPT NOTATION ###

# TODO:
# Comments with # (DONE)
# Exception handling in the parsing process instead of executing process (DONE)
# Variable handling in the executing process instead of parsing process (DONE)
# Get property for any py object .......... Future me here. Das wicked niggster, hell, add a fucking eval operator (DONE)
# Call any py object's method ............. Future me here again. No words (DONE)
# Nigusi O_O (DONE)
# Custom, human comprehensible fucking split function (DONE)
# Bring back variable getter (DONE)
# Detours with > or perhaps with separate command (idk, more of a frontend task) (DONE)
# Variable setting from commands that return a value (DONE)
# Union parameters (DONE)
# Scopes O_O powered by scoped_split()
# Operations on variables O_O
# Transition @ to an operator
# Add switch/if statemetents or at least ternery operators
# Include the line number in raised exceptions

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

	# Complete the data that wasn't processed in the main loop
	word += escape_next
	if len(word):
		buffer.append(word)

	# Just a compatibility feature
	if expect_quote:
		raise SyntaxError(f'Expected closing {expect_quote}.')

	return buffer

class Context:
	_instructions = {}
	_globals = {}
	
	# A map of all registered instructions in the context
	# Note: the dictionary is immutable to the context
	def instructions(self):
		return self._instructions.copy()
	
	# A map of all globals in the context
	# Note: the dictionary is immutable to the context
	def globals(self):
		return self._globals.copy()

	# Registers a new command with a given alias and a function that is called when the instruction is invoked
	# The function can be both asynchronous and generic
	# Use hints to automatically convert string arguments into respective types
	def register(self, alias: str, fn: Callable):
		self._instructions[alias] = fn
	
	# Retrieves a variables value
	async def getvar(self, alias: str):
		val = None

		try:
			val = self._globals[alias]
		except KeyError:
			raise VarIndexError(f'"{alias}" was not recognised as a variable!')
		
		return val
	
	# Assigns a value to or declares a variable
	async def setvar(self, alias: str, value: str):
		if value is None:
			raise VarAssignError(f'cannot assign VOID to "{alias}"! Variable remains unchanged.')

		self._globals[alias] = value

	# Parses and executes code one line at a time
	async def interpret_line(self, line: str, line_number: int = 0, escapes: str = '\\', variable_notes: str = '@'):
		from inspect import iscoroutinefunction as is_async
		from inspect import signature as Signature
		from inspect import Parameter
		from types import UnionType

		words = split(line, escapes=escapes)
		if not len(words): return
		
		alias = words[0]
		args = words[1:]

		# Replace all arguments starting with @ with global values 
		for i, arg in enumerate(args):
			if not len(arg):
				continue

			if arg[0] in variable_notes:
				if len(arg) < 2:
					raise SyntaxError(f'Expected variable name after {arg[0]}')

				args[i] = await self.getvar(arg[1:])
			elif len(arg) > 1 and arg[0] in escapes and arg[1] in variable_notes:
				# Handle escaped @ character
				args[i] = arg[1:]

		fn = None
		
		# Search for a command with the given alias
		try:
			fn = self._instructions[alias]
		except KeyError:
			raise CmdIndexError(f'"{alias}" was not recognised as a command!')
		
		# Cast all args based on the command's function signature
		sig = Signature(fn)
		for i, param_name in enumerate(sig.parameters.keys()):
			param = sig.parameters[param_name]
			t = param.annotation
			kind = param.kind
			
			# Keyword parameters are inaccessible
			if kind == Parameter.KEYWORD_ONLY or kind == Parameter.VAR_KEYWORD:
				continue
			
			if not t == Parameter.empty:
				def cast(arg_i, types):
					def to_iter(obj):
						try:
							return iter(obj)
						except TypeError:
							return iter([obj])
					
					for t in to_iter(types):
						try:
							args[arg_i] = t(args[arg_i])
						except IndexError:
							if param.default == Parameter.empty:
								raise CastError(f'Missing argument "{param_name}" of type "{t.__name__}"!')
							return True
						except ValueError:
							if t is types[-1]:
								raise CastError(f'Unable to convert "{args[arg_i]}" to type "{t.__name__}"! Parameter {arg_i} : "{param_name}".')
							continue

						return False

				if kind == Parameter.VAR_POSITIONAL:
					for ii in range(len(args[i:])):
						if type(t) is UnionType:
							cast(i + ii, t.__args__)
						else:
							cast(i + ii, t)
				else:
					if type(t) is UnionType:
						cast(i, t.__args__)
					else:
						if cast(i, t):
							break
		
		# Execute the command
		res = None
		if is_async(fn):
			res = await fn(*args)
		else:
			res = fn(*args)
		
		return res

	# Splits text into a list of lines then interprets them
	async def interpret(self, text: str):
		lines = split(text, delimiters=';\n', quotes='', comments='', escapes='')
		if not len(lines): return
		
		for line in lines:
			if not len(line): continue
			await self.interpret_line(line)
