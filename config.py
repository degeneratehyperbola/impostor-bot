import json

CFG_TOKEN = 'BotToken'
CFG_CHANNELID = 'ChannelID'

class Config:
	_config = {}
	path = 'config.json'

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

	def _ensure_file(self):
		from os.path import exists
		if not exists(self.path):
			open(self.path, 'r').close()

	def save(self):
		self._ensure_file()

		with open(self.path, 'w') as file:
			file.write(json.dumps(self._config, sort_keys=True, indent="\t"))

	def load(self):
		self._ensure_file()

		buffer = None
		with open(self.path, 'r') as file:
			buffer = json.loads(file.read())

		if type(buffer) is dict:
			self._config = buffer
