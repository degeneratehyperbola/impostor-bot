import json

CFG_TOKEN = 'BotToken'
CFG_VCHANNELID = 'VoiceChannelID'
CFG_TCHANNELID = 'TextChannelID'

class Config(dict):
	path = 'config.json'

	def __init_subclass__(cls):
		return super().__init_subclass__()

	def _ensure_file(self):
		from os.path import exists
		if not exists(self.path):
			open(self.path, 'r').close()

	def save(self):
		self._ensure_file()

		with open(self.path, 'w') as file:
			file.write(json.dumps(self, sort_keys=True, indent="\t"))

	def load(self):
		self._ensure_file()

		buffer = None
		with open(self.path, 'r') as file:
			buffer = json.loads(file.read())

		if type(buffer) is dict:
			self.update(buffer)
