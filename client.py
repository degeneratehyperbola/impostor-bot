from typing import Coroutine, Generator
from log import *
import discord

class Client(discord.Client):
	tasks = []
	
	def create_task(self, coro: Coroutine | Generator):
		task = self.loop.create_task(coro)
		self.tasks.append(task)
		return task

	async def close(self):
		error("Shutting down...")
		
		for task in self.tasks:
			if not task.done(): task.cancel()
			
		return await super().close()
	
	async def on_ready(self):
		notice('Client connected')
