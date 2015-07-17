import zmq
import json
import messages

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://127.0.0.1:4444")

def build_client(socket):
	def send_message(msg):
		socket.send_string(json.dumps(msg))
	return send_message

send = build_client(socket)

send(messages.list)
