from client import *
from config import *
from isn import *
from threading import Thread

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
			error('Unknown current channel. Use "setch" command to set a new current channel')
			return True

async def check_text_channel():
	if await check_channel(): return True

	if not hasattr(current_channel, 'send') and not hasattr(current_channel, 'history'):
		error('Current channel is not a text channel')
		return True

async def check_voice_channel():
	if await check_channel(): return True
	
	if not isinstance(current_channel, discord.VoiceChannel):
		error('Current channel is not a voice channel')
		return True

async def check_voice_client():
	if await check_voice_channel(): return True

	if not current_channel.guild.voice_client:
		try:
			await join_channel()
		except:
			error(f'Unknown error occured while connecting to "{current_channel.guild.name}"')
			return

### GARBAGE COLLECTOR ###

async def clear_cache():
	from os import remove
	try:
		remove('cache')
	except Exception as e:
		error(e)
		return

	notice('Cache successfully cleared')

### COMMANDS ###

async def cmdlist(*msgs: str):
	bold('List of registered commands')
	
	for key in isn_context.cmds().keys():
		echo(key)

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
					error('Invalid channel/user ID!')
					return

	global current_channel
	current_channel = channel
	
	notice(f'Current channel set to {type(channel).__name__} "{channel.name}"')

	config[CFG_CHANNELID] = channel_user_id
	config.save()

async def sendmsg(*msgs: str):
	if await check_text_channel(): return

	await current_channel.send(' '.join(msgs))

async def join_channel():
	if await check_voice_channel(): return

	try:
		await current_channel.connect()
	except discord.ClientException:
		error('Unable to connect! Voice client is already connected')

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
					error('Invalid channel/guild ID!')
					return
	
	if not guild:
		guild = channel.guild

	if not guild.voice_client:
		error(f'Not connected in "{guild.name}"')
		return

	await guild.voice_client.disconnect()

def play_audio(path: str):
	from os.path import exists
	if not exists(path):
		error(f'Could not find {path}')
		return

	try:
		current_channel.guild.voice_client.play(discord.FFmpegPCMAudio(source=path))
	except discord.ClientException:
		error('Already playing audio')
		return

def download_play_audio(url: str):
	from youtube_dl import YoutubeDL
	path = None
	with YoutubeDL({'outtmpl': 'cache\%(title)s-%(id)s.%(ext)s', 'format': 'bestaudio', 'nooverwrites': True, 'quiet': True, 'noplaylist': True}) as ytdl:
		try:
			result = ytdl.extract_info(url)
			path = ytdl.prepare_filename(result)
		except:
			error('Unable to download audio')
			return
		
	play_audio(path)

async def audio_fs(path: str):
	if await check_voice_client(): return

	Thread(target=play_audio, args=(path,)).start()

async def audio_web(url: str):
	if await check_voice_client(): return

	Thread(target=download_play_audio, args=(url,)).start()

async def stop_audio():
	if await check_voice_client(): return
	
	current_channel.guild.voice_client.stop()

async def pause_audio():
	if await check_voice_client(): return

	current_channel.guild.voice_client.pause()

async def resume_audio():
	if await check_voice_client(): return

	current_channel.guild.voice_client.resume()

async def username(user_id: int):
	user = client.get_user(user_id)
	
	if not user:
		try:
			user = await client.fetch_user(user_id)
		except discord.NotFound:
			error('Invalid user ID!')
			return
	
	return f'{user.name}#{user.discriminator}'

async def delete_num(count: int = 5):
	if await check_text_channel(): return

	deleted = 0
	
	async for message in current_channel.history(limit=count):
		await message.delete()
		deleted += 1
	
	notice(f'Successfully deleted {deleted} message(s)')

async def delete_last():
	if await check_text_channel(): return

	message = None
	
	try:
		message = await current_channel.history(limit=100).find(lambda m: m.author.id == client.user.id)
	except:
		error('Last message too far or not found!')
		return
	
	await message.delete()
	notice('Successfully deleted 1 message')

async def msg_history(count: int = 5):
	if await check_text_channel(): return

	last = None
	msgs = await current_channel.history(limit = count).flatten()
	msgs.reverse()
	
	if not len(msgs):
		notice('No messages in record')
		return
	
	try:
		for m in msgs:
			user = await username(m.author.id)
			
			if last != user:
				notice(user, '\t', m.created_at)
			
			echo(m.content)
			
			last = user
	except Exception as e:
		error(e)

async def nop(*args):
	pass

async def eval_e(*args):
	try:
		eval(' '.join(args))
	except Exception as e:
		error(e)

### ENTRY POINT ###

async def command_prompt():
	await client.wait_until_ready()
	
	from time import sleep
	sleep(.3)

	while True:
		try:
			await isn_context.parse(await ainput('>'))
		except Exception as e:
			error(e)

def main():
	global client
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
	isn_context.register('pause', pause_audio)
	isn_context.register('resume', resume_audio)

	isn_context.register('set', isn_context.setvar)
	isn_context.register('get', isn_context.getvar)

	isn_context.register('clrcache', clear_cache)

	notice(f'Successfully registered {len(isn_context.cmds())} commands. Type "help" to see a full list of instructions')
	print('Connecting...')

	config.load()

	client.create_task(command_prompt())

	try:
		client.loop.run_until_complete(client.start(config[CFG_TOKEN]))
	except TypeError or KeyError:
		error(f'Missing bot token in {CFG_PATH}')
	except discord.LoginFailure:
		error(f'Invalid bot token in {CFG_PATH}')
	except KeyboardInterrupt:
		client.loop.run_until_complete(client.close())
	except:
		pass

if __name__ == '__main__':
	main()
