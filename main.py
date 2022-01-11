#! venv/bin/python
import os 
import numpy as np
import cv2 

VIDEO_PATH = "./attachments/bad_apple.mp4"
WIDTH = 50
SIZE = (WIDTH, WIDTH*480//640)

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

	string = stringified.replace("0", " ").replace("1", '*')
	return string

def print_terminal(string):
	os.system('clear')
	print(string)

def get_stream():
	cap = cv2.VideoCapture(VIDEO_PATH)

	success, img = cap.read()
	while success:
		
		img = prep_img(img)
		string = to_string(img)
		print_terminal(string)

		success, img = cap.read()

		cv2.imshow('Bad Apple', img)
		
		if cv2.waitKey(25) & 0xff == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
	

if __name__ == "__main__":
	get_stream()