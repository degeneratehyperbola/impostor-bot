from client import *
from config import *
from log import *
from isn import *
from threading import Thread

# TODO:
# Command prompt always on the bottom

isn_context = Context()
config = Config()
client = None
current_channel = None

### CHECKS ###

async def check_channel():
	if not current_channel:
		try:
			await set_channel(config[CFG_CHANNELID])
		except:
			raise Exception('Unknown current channel. Use "setch" command to set a new current channel')

async def check_text_channel():
	await check_channel()

	if not hasattr(current_channel, 'send') and not hasattr(current_channel, 'history'):
		raise Exception('Current channel is not a text channel')

async def check_voice_channel():
	await check_channel()
	
	if not isinstance(current_channel, discord.VoiceChannel):
		raise Exception('Current channel is not a voice channel')

async def check_voice_client():
	await check_voice_channel()

	if not current_channel.guild.voice_client:
		await join_channel()

### GARBAGE COLLECTOR ###

def clear_cache():
	from os import remove
	remove('cache')

	notice('Cache successfully cleared')

### COMMANDS ###

def cmdlist(*msgs: str):
	bold('List of registered commands')
	echo(*isn_context.cmds().keys(), sep='\n')

async def set_channel(channel_user_id: int):
	channel = client.get_channel(channel_user_id)
	
	if not channel:
		channel = client.get_user(channel_user_id)
		
		if not channel:
			try:
				channel = await client.fetch_channel(channel_user_id)
			except:
				try:
					channel = await client.fetch_user(channel_user_id)
				except discord.NotFound:
					raise Exception('Invalid channel/user ID!')

	global current_channel
	current_channel = channel
	
	notice(f'Current channel set to {type(channel).__name__} "{channel.name}"')

	config[CFG_CHANNELID] = channel_user_id
	config.save()

async def sendmsg(*msgs: str):
	await check_text_channel()

	await current_channel.send(' '.join(msgs))

async def join_channel():
	await check_voice_channel()

	try:
		await current_channel.connect()
	except discord.ClientException:
		raise Exception('Unable to connect! Voice client is already connected')

async def leave_all_voice_channels():
	left = 0

	for voice_client in client.voice_clients:
		if voice_client.is_connected():
			await voice_client.disconnect()
			left += 1
	
	notice(f'Left {left} voice channel(s)')

async def leave_voice_channel(channel_guild_id: int):
	guild = None
	channel = client.get_channel(channel_guild_id)

	if not channel:
		guild = client.get_guild(channel_guild_id)

		if not guild:
			try:
				channel = await client.fetch_channel(channel_guild_id)
			except discord.NotFound:
				try:
					guild = await client.fetch_guild(channel_guild_id)
				except discord.NotFound:
					raise Exception('Invalid channel/guild ID!')
	
	if not guild:
		guild = channel.guild

	if not guild.voice_client:
		raise Exception(f'Not connected in "{guild.name}"')

	await guild.voice_client.disconnect()

now_playing = ''
audio_stack = []

def process_audio_stack(e: Exception = None):
	global now_playing
	now_playing = ''

	if len(audio_stack):
		next_audio = audio_stack[0]
		del audio_stack[0]
		play_audio(next_audio)
	else:
		notice('Reached the end of the audio queue')

def list_audio_stack():
	from os.path import basename
	bold(f'Audio queue contains {len(audio_stack)} item(s)')
	echo(*[basename(i) for i in audio_stack], sep='\n')
	bold('Now playing')
	echo(basename(now_playing))

def play_audio(path: str):
	vc = current_channel.guild.voice_client

	if vc.is_playing():
		notice(f'Added {path} to the queue')
		audio_stack.append(path)
		return

	try:
		global now_playing
		now_playing = path
		vc.play(discord.FFmpegPCMAudio(source=path), after=process_audio_stack)
	except Exception as e:
		error(e)
		return

def download_play_audio(url: str):
	from youtube_dl import YoutubeDL
	path = None
	with YoutubeDL({'outtmpl': 'cache\%(title)s-%(id)s.%(ext)s', 'format': 'bestaudio', 'nooverwrites': True, 'quiet': True, 'noplaylist': True}) as ytdl:
		try:
			result = ytdl.extract_info(url)
			path = ytdl.prepare_filename(result)
		except Exception as e:
			error(e)
			return
		
	play_audio(path)

def play_audio_sel(path_filter: str):
	from glob import glob
	from os.path import isfile

	sel = [p for p in glob(path_filter, recursive=True) if isfile(p)]
	if len(sel):
		global audio_stack
		audio_stack += sel
		notice(f'Added {len(sel)} files to the queue')
	else:
		error(f'Could not match "{path_filter}"')
		return

	vc = current_channel.guild.voice_client

	if not vc.is_playing():
		process_audio_stack()

async def audio_fs(path: str):
	await check_voice_client()

	Thread(target=play_audio_sel, args=(path,)).start()

async def audio_web(url: str):
	await check_voice_client()

	Thread(target=download_play_audio, args=(url,)).start()

async def stop_audio():
	await check_voice_client()

	global now_playing
	now_playing = ''
	audio_stack.clear()
	current_channel.guild.voice_client.stop()

async def skip_audio():
	await check_voice_client()
	
	current_channel.guild.voice_client.stop()

async def pause_audio():
	await check_voice_client()

	current_channel.guild.voice_client.pause()

async def resume_audio():
	await check_voice_client()

	current_channel.guild.voice_client.resume()

async def username(user_id: int):
	user = client.get_user(user_id)
	
	if not user:
		try:
			user = await client.fetch_user(user_id)
		except discord.NotFound:
			raise Exception('Invalid user ID!')
	
	return f'{user.name}#{user.discriminator}'

async def delete_num(count: int = 5):
	await check_text_channel()

	deleted = 0
	
	async for message in current_channel.history(limit=count):
		await message.delete()
		deleted += 1
	
	notice(f'Successfully deleted {deleted} message(s)')

async def delete_last():
	await check_text_channel()

	message = None
	
	try:
		message = await current_channel.history(limit=100).find(lambda m: m.author.id == client.user.id)
	except:
		raise Exception('Last message too far or not found!')
	
	await message.delete()
	notice('Successfully deleted 1 message')

async def msg_history(count: int = 5):
	await check_text_channel()

	last = None
	msgs = await current_channel.history(limit = count).flatten()
	msgs.reverse()
	
	if not len(msgs):
		raise Exception('No messages in record')
	
	try:
		for m in msgs:
			user = await username(m.author.id)
			
			if last != user:
				notice(user, '\t\t', m.created_at)
			
			echo(m.content)
			
			last = user
	except Exception as e:
		error(e)

def nop(*args):
	pass

def eval_e(*args):
	eval(' '.join(args))

### COMMAND PROMPT ###

async def ainput(prompt: str = '') -> str:
	import asyncio
	from concurrent.futures import ThreadPoolExecutor

	with ThreadPoolExecutor(1) as executor:
		return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)

async def command_prompt():
	await client.wait_until_ready()
	
	from time import sleep
	sleep(.35)

	while True:
		try:
			await isn_context.interpret(await ainput('> '))
		except Exception as e:
			error(e)

### ENTRY POINT ###

if __name__ == '__main__':
	client = Client()

	isn_context.register('help', cmdlist)

	isn_context.register('echo', echo)
	isn_context.register('ntc', notice)
	isn_context.register('err', error)
	isn_context.register('bold', bold)
	isn_context.register('cls', clear)
	isn_context.register('pos', cur_pos)

	isn_context.register('input', ainput)
	isn_context.register('nop', nop)
	isn_context.register('rem', nop)
	isn_context.register('eval', eval_e)

	isn_context.register('break', client.close)

	isn_context.register('uname', username)

	isn_context.register('setch', set_channel)
	isn_context.register('msg', sendmsg)
	isn_context.register('unmsg', delete_last)
	isn_context.register('delmsg', delete_num)
	isn_context.register('chatlog', msg_history)

	isn_context.register('join', join_channel)
	isn_context.register('leaveall', leave_all_voice_channels)
	isn_context.register('leave', leave_voice_channel)
	isn_context.register('play', audio_fs)
	isn_context.register('playweb', audio_web)
	isn_context.register('stop', stop_audio)
	isn_context.register('skip', skip_audio)
	isn_context.register('pause', pause_audio)
	isn_context.register('resume', resume_audio)
	isn_context.register('aq', list_audio_stack)

	isn_context.register('set', isn_context.setvar)
	isn_context.register('get', isn_context.getvar)

	isn_context.register('clrcache', clear_cache)

	notice(f'Successfully registered {len(isn_context.cmds())} commands. Type "help" to see a full list of instructions')
	echo('Connecting...')

	try:
		config.load()
	except Exception as e:
		error(e)
		exit()

	client.create_task(command_prompt())

	try:
		client.loop.run_until_complete(client.start(config[CFG_TOKEN]))
	except TypeError or KeyError:
		error(f'Missing bot token in {config.path}')
	except discord.LoginFailure:
		error(f'Invalid bot token in {config.path}')
	except KeyboardInterrupt:
		client.loop.run_until_complete(client.close())
	except Exception as e:
		error(e)
		exit()
