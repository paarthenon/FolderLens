import zmq
import time
import json
import os, sys

class Repo(object):
	"""docstring for Repo"""
	def __init__(self, path):
		super(Repo, self).__init__()
		self.path = path
		self.mapping = {}

	def refresh(self):
		self.mapping = {}
		for current_path, dirs, files in os.walk(self.path):
			for file in files:
				source_path = os.path.join(current_path, file)
				relative_path = os.path.relpath(source_path, source_root)
				self.mapping[relative_path] = source_path

	def get_mapping(self):
		if not self.mapping:
			self.refresh()
		return self.mapping

class Lens(object):
	"""docstring for Lens"""
	def __init__(self, out_dir, repos):
		super(Lens, self).__init__()
		self.out_dir = out_dir
		self.repos = repos

	def add_repo(self, repo):
		self.repos.append(repo)

	def write(self):
		def merge_mappings(dict_list):
			merged = {}
			duplicates = {}
			for dict in dict_list:
				for dest, source in dict.items():
					if dest in duplicates:
						duplicates[dest].append(source)
					else:
						if dest in merged:
							duplicates[dest] = [merged.pop(dest), source]
						else:
							merged[dest] = source
			return merged, duplicates

		merged, duplicates = merge_mappings([repo.get_mapping() for repo in self.repos])

		def write_symlinks(dict):
			for rel_path, source_path in dict.items():
				dest_path = os.path.join(self.out_dir, rel_path)
				os.makedirs(os.path.dirname(dest_path), exist_ok=True)
				os.symlink(source_path, dest_path)

		write_symlinks(merged)

def command_list(state, msg):
	print("List command!")

route =	\
{
	'list': command_list
}

def load_config():
	with open('config.json') as cfg:
		return json.load(cfg)

def get_socket(port):
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	socket.bind("tcp://*:%s" % port)
	return socket

def main():
	config = load_config()
	socket = get_socket(config['port'])

	while True:
		msg_str = socket.recv_string()
		print(msg_str)
		msg = json.loads(msg_str)
		print("Type: %s " % msg['type'])

		route[msg['type']](config, msg)

		time.sleep(1)

if __name__ == '__main__':
	main()