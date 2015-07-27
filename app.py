class Repo:
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

	def __str__(self):
		return "  Repo source: %s\n" % repo.path

class Lens:
	#TODO: track dirty edits
	def __init__(self, out_dir, repos):
		super(Lens, self).__init__()
		self.out_dir = out_dir
		self.repos = repos

	def add_repo(self, repo):
		self.repos.append(repo)

	def ensure_folder(self):
		os.makedirs(self.out_dir, exist_ok=True)

	def __str__(self):
		header = "Lens with output dir: %s\n" % lens.out_dir
		for repo in self.repos:
			header = header + repo
		return header

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

class State:
	def __init__(self, config_path):
		config = load_config(config_path)
		self.construct(config)

	def construct(self, config):
		self.lenses = []
		lensdefs = cfg['lenses']
		for lens in lensdefs.keys():
			repos = [Repo(repo) for repo in lensdefs[lens]]
			self.lenses.append(Lens(lens, repos))

	@staticmethod
	def load_config():
		with open('config.json') as cfg:
			return json.load(cfg)

	def __str__(self):
		header = "Listening lenses and repos\n"
		for lens in self.lenses:
			header = header + lens
