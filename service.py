import zmq
import time
import json

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