class NameCollision(Exception):
	pass

class PathCollision(Exception):
	pass

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
		return "  Repo source: %s\n" % self.path

class Lens:
	#TODO: track dirty edits
	def __init__(self, name, path, repos):
		super(Lens, self).__init__()
		self.name = name
		self.path = path
		self.repos = repos

	def add_repo(self, repo):
		self.repos.append(repo)
		return self

	def ensure_folder(self):
		os.makedirs(self.path, exist_ok=True)
		return self

	def __str__(self):
		header = "Lens with output dir: %s\n" % self.path
		for repo in self.repos:
			header = header + str(repo)
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
				dest_path = os.path.join(self.path, rel_path)
				os.makedirs(os.path.dirname(dest_path), exist_ok=True)
				#take this out, eventually
				if not os.path.isfile(dest_path):
					os.symlink(source_path, dest_path)
				else:
					print("File already exists: %s" % dest_path)

		write_symlinks(merged)

class LensRegistry:
	def __init__(self):
		self._by_name = {}
		self._by_path = {}

	def add_lens_obj(self, lens):
		if(lens.name in self._by_name):
			raise NameCollision("Name [%s] already exists in registry" % lens.name)
		if(lens.path in self._by_path):
			raise PathCollision("Path [%s] already exists in registry" % lens.path)
		self._by_name[name] = lens
		self._by_path[path] = lens
		return self

	def add_lens(self, name, path):
		if(name in self._by_name):
			raise NameCollision("Name [%s] already exists in registry" % name)
		if(path in self._by_path):
			raise PathCollision("Path [%s] already exists in registry" % path)
		lens = Lens(name, path, [])
		self._by_name[name] = lens
		self._by_path[path] = lens
		return lens

	def get_lens(self, string):
		if(string in self._by_name):
			return self._by_name[string]
		if(string in self._by_path):
			return self._by_path[string]
		return None

	def __str__(self):
		string = "Listening lenses and repos\n"
		for lens in self._by_name.values():
			string = string + str(lens)
		return string
