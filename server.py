import zmq
import time
import json
import os, sys, signal

from router import Router
from app import Repo, Lens, LensRegistry

router = Router()

@router.register('list')
def command_list(state, msg):
	print(state)

@router.register('stop')
def command_stop(state, msg):
	print("Thank you, goodbye")
	sys.exit(0)

def get_socket(port):
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	socket.bind("tcp://*:%s" % port)
	return socket

def construct_from_config(config_path):
	cfg = {}
	with open(config_path) as config:
		cfg = json.load(config)

	registry = LensRegistry()

	lensdefs = cfg['lenses']
	for lens_name in lensdefs.keys():
		repos = [Repo(repo) for repo in lensdefs[lens_name]['repos']]
		lens_dir = lensdefs[lens_name]['output']
		lens = registry.add_lens(lens_name, lens_dir)
		for repo_dir in lensdefs[lens_name]['repos']:
			lens.add_repo(Repo(repo_dir))
			#TODO: fix the inconsistency between being able to add a constructed
			#repo vs. adding a constructed lens
	return registry

def run(socket, handler):
	while True:
		msg_str = socket.recv_string()
		print(msg_str)
		msg = json.loads(msg_str)

		if handler(msg):
			#send reply
			pass

		time.sleep(1)

def main():
	socket = get_socket(4444)

	registry = construct_from_config('config.json')

	def handler(msg):
		router.dispatch(msg['type'])(registry, msg)

	run(socket, handler)

if __name__ == '__main__':
	main()
