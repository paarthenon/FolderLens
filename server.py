import zmq
import time
import json
import os, sys, signal

from router import Router
from app import Repo, Lens

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

def load_config():
	with open('config.json') as cfg:
		return json.load(cfg)

def construct(registry, config_path):
	cfg = load_config(config_path)
	lensdefs = cfg['lenses']
	for lens_name in lensdefs.keys():
		repos = [Repo(repo) for repo in lensdefs[lens_name]['repos']]
		lens_dir = lensdefs[lens_name]['output']
		lens = registry.add_lens(lens_name, lens_dir)
		for repo_dir in lensdefs[lens_name]['repos']:
			lens.add_repo(Repo(repo_dir))
			#TODO: fix the inconsistency between being able to add a constructed
			#repo vs. adding a constructed lens

def main():
	config = load_config()
	socket = get_socket(4444)

	state = State('config.json')

	while True:
		msg_str = socket.recv_string()
		print(msg_str)
		msg = json.loads(msg_str)
		print("Type: %s " % msg['type'])

		function = router.dispatch(msg['type'])
		function(state, msg)

		time.sleep(1)

if __name__ == '__main__':
	main()
