import zmq
import time
import json
import os, sys, signal

class Repo:
	"""docstring for Repo"""
	def __init__(self, path):
		super(Repo, self).__init__()
		self.path = path

	def get_mapping(self):
		mapping = {}
		for current_path, dirs, files in os.walk(self.path):
			for file in files:
				source_path = os.path.join(current_path, file)
				relative_path = os.path.relpath(source_path, source_root)
				mapping[relative_path] = source_path
		return mapping

class Lens:
	#TODO: track dirty edits
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
				#take this out, eventually
				if not os.path.isfile(dest_path):
					os.symlink(source_path, dest_path)
				else:
					print("File already exists: %s" % dest_path)

		write_symlinks(merged)

class SvcState:
	def __init__(self, cfg):
		self.lenses = []
		lensdefs = cfg['lenses']
		for lens in lensdefs.keys():
			repos = [Repo(repo) for repo in lensdefs[lens]]
			self.lenses.append(Lens(lens, repos))


def command_list(state, msg):
	print("Listening lenses and repos")
	for lens in state.lenses:
		print("Lens with output dir: %s" % lens.out_dir)
		for repo in lens.repos:
			print("  Repo source: %s" % repo.path)

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

def signal_handler(signal, frame):
	print("Thank you, goodbye")
	sys.exit(0)

def main():
	config = load_config()
	socket = get_socket(config['port'])

	state = SvcState(config)

	while True:
		msg_str = socket.recv_string()
		print(msg_str)
		msg = json.loads(msg_str)
		print("Type: %s " % msg['type'])

		route[msg['type']](state, msg)

		time.sleep(1)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	main()
