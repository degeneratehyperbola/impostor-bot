# Impostor Discord Bot

A programmable Discord bot controlled using an POSIX-like syntax. It has generic functionality of every Discord bot ever but is controlled from the host and not through chat commands. This human interface is pretty bad for some stuff like text messaging or talking in a voice chat, although still alows to do so.

# The Idea
The primal idea for it was to have yet another way of making Your own discord bot that is so easy to program, so high-level, that it loses all its purpose. Hence it is controlled by Impostor Script Notation that was made in, like, 3 minutes with simple POSIX argument parsing.

And yes, it delivers on the promise of doing a little trolling.

# Usage
This repository contains `example.py` file which might seem to be the example but, in fact, holds most of the bot's functionality and the entry point. If You want to just no-brain run it, run aforesaid `example.py` file

## Syntax
A simple POSIX-like syntax with no super advanced stuff like dumps or nesting.

```ps1
<command> [argument1] [argument2] [argument3]...
```

Grouping is done with quotes:
```ps1
<command> "argument ... still the same argument" "now goes the next one"

# Parsed as: ['argument ... still the same argument', 'now goes the next one']
```

And escaping with a `\` (backslash) like so:
```ps1
<command> "i can have \"funny\" symbols in here, including the \\"

# Parsed as: ['i can have "funny" symbols in here, including the \']
```

There is also a support for variables but, currently, no way of setting them using implemented instructions.

Set an existing variable or declare a new one:
```ps1
<variable_name> = <value>
```

Retrieve the value from a declared variable:
```ps1
<command> [arguments] @<variable_name> [arguments]...
```

Comments are not yet implemented.

## Examples
Read the chat for signs of life (last 10 messages):
```ps1
setch 746316046616625192
chatlog 10
```

Send a chat message:
```ps1
setch 746316046616625192
msg "Hello? Is this chat dead?"
msg "Gonna play some music on #townhall"
```

Play audio from web and from the filesystem:
```ps1
setch 811264974184775691
join
playweb https://www.youtube.com/watch?v=MH1imROLPho&list=PLYZCCGiDf0qijxmpClFxZlVWWyzuwjy2y&index=1
stop
play "D:\Music\Bad Piggies Soundtrack.m4a"
```

## Instruction Set
You can see the list of all implemented commands using the `help` command, however they are not yet documented :P

# TODO List
Each module's TODO list is in their respective files.

[ISN TODO List](https://github.com/degeneratehyperbola/ImpostorBot/blob/2429304202cba5416dabc120485fa99ca36faa1f/isn.py#L128-L135)
