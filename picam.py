# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 42
rawCapture = PiRGBArray(camera, size=camera.resolution)
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
n=1

checktimeBefore = int(time.strftime('%S'))
FPS_list = []
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	# show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	

	FPS_list.append(1)
	checktime = int(time.strftime('%S'))
	if checktime - checktimeBefore == 1 or checktime - checktimeBefore == -59:
		print("FPS :", len(FPS_list))
		FPS_list = []
		checktimeBefore = checktime
		
	if key == ord("q"):
		break
	elif key == ord("\t"):
		camera.capture('output'+str(n)+'.jpg')
		n = n + 1