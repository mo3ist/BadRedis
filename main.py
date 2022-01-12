#! venv/bin/python
import os 
import argparse
import numpy as np
import cv2 
import redis 

VIDEO_PATH = "./attachments/bad_apple.mp4"
assert os.path.exists

WIDTH = 50
SIZE = (WIDTH, WIDTH*480//640)
DELIMITER = "+"
REDIS_CHANNEL = 'badredis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

def prep_img(img):
	# Get one channel: Gray
	grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Resize
	resized = cv2.resize(grayed,SIZE,fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
	return resized

def to_string(img):
	# Get the binary threshold (0 for black, 1 for white)
	thresh_arr = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY)[1]

	# Joining the 2d array
	stringified = "\n".join(
		[" ".join(x) for x in thresh_arr.astype(str)]
	)

	string = stringified.replace("0", " ").replace("1", DELIMITER)
	return string

def print_to_terminal(string):
	os.system('clear')
	print(string)

def get_stream():
	# Get a stringified stream of the video 

	cap = cv2.VideoCapture(VIDEO_PATH)

	success, img = cap.read()
	while success:
		
		img = prep_img(img)
		string = to_string(img)
		yield string

		success, img = cap.read()

		cv2.imshow('Bad Apple', img)
		
		if cv2.waitKey(25) & 0xff == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
	return

def connect():
	r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

	try:
		# check the connection
		r.ping()
		pubsub = r.pubsub(ignore_subscribe_messages=True) 
		return r, pubsub

	except:
		return None, None

def act_as_client():
	r, ps = connect()

	ps.subscribe(REDIS_CHANNEL)
	for msg in ps.listen():
		print_to_terminal(msg["data"].decode('utf-8'))

def act_as_server():
	# Get the redis instance and the pubsub instance
	r, _ = connect()
	if not r:
		return

	# Get the stringified video stream
	stream = get_stream()

	for frame in stream:
		# Send the frame to the client[s]
		r.publish(REDIS_CHANNEL, frame)

	return 

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run 'Bad Apple' with Redis Pub/Sub.")
	parser.add_argument("-s", "--server", help="runs the script in server mode.", action='store_true')
	parser.add_argument("-c", "--client", help="runs the script in client mode.", action='store_true')

	args = parser.parse_args()

	try:
		# Can't be server AND client at the same time
		assert (args.server ^ args.client)
		
		if args.server:
			act_as_server()

		elif args.client:
			act_as_client()

	except:
		parser.print_help()
