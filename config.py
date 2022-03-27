import json

CFG_PATH = "config.json"
CFG_CHANNELID = "ChannelID"
CFG_TOKEN = "BotToken"

class Config:
	_config = {}

### OVERRIDES ###

	def __getitem__(self, key: str):
		return self._config[key]
	
	def __setitem__(self, key: str, value):
		self._config[key] = value

	def __delitem__(self, key: str):
		del self._config[key]

	def __contains__(self, key: str):
		return key in self._config.keys()
	
	def items(self):
		return self._config.items()
		
	def keys(self):
		return self._config.keys()

	def values(self):
		return self._config.values()

### SAVE & LOAD ###

	def ensure_file(self):
		from os.path import exists
		if not exists(CFG_PATH):
			open(CFG_PATH, "r").close()

	def save(self):
		self.ensure_file()

		with open(CFG_PATH, "w") as file:
			file.write(json.dumps(self._config, sort_keys=True, indent=4))
			file.close()

	def load(self) -> bool:
		self.ensure_file()

		buffer = None
		with open(CFG_PATH, "r") as file:
			try:
				buffer = json.loads(file.read())
			except:
				pass
			finally:
				file.close()

		if type(buffer) is dict:
			self._config = buffer
			return True
		
		return False
