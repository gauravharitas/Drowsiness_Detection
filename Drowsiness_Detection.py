
# Importing necessary libraries
from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
from pygame import mixer 
import sqlite3
import matplotlib.pyplot as plt
import time
import numpy as np
import Creds


# Sending Messages to the Respective Owner
from twilio.rest import Client
# Twilio account SID and auth token

#please refer Creds.py File which contain => account_sid, auth_token, from_number, to_number

# Create a Twilio client
client = Client(Creds.account_sid, Creds.auth_token)

# The phone number we want to send the SMS to

# to_number -> in Creads.py

# The phone number we purchased from Twilio or the Twilio trial number

# from_number -> in Creads.py



# Initialising Database to store Images
MyDB = sqlite3.connect('Drowsy.db')
MyCursor=MyDB.cursor()


MyCursor.execute("CREATE TABLE IF NOT EXISTS Images (id INTEGER PRIMARY KEY AUTOINCREMENT, Photo BLOB NOT NULL)")

# Initialising alert sound
mixer.init()
sound = mixer.Sound('alarm.wav')
yawn = mixer.Sound('yawn.mp3')
alert = mixer.Sound('alert.mp3')


# Driver's Eye Aspect Ratio
def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

# Mouth's Aspect Ratio
def mouth_aspect_ratio(mouth):
	A = distance.euclidean(mouth[1], mouth[7])
	B = distance.euclidean(mouth[3], mouth[5])
	C = distance.euclidean(mouth[0], mouth[4])
	mar = (A + B) / (2.0 * C)
	return mar

# EAR Threshold Value
ethresh = 0.22
frame_check = 20

# MAR Threshold Value
mthresh = 0.6


detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")      # Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"] #[36, 37, 38, 39, 40, 41]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]#[42, 43, 44, 45, 46, 47]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["inner_mouth"]#[60, 61, 62, 63, 64, 65, 66, 67, 68]
# print(mStart)
# print(mEnd)

# Live Camera Frame Capture
cap=cv2.VideoCapture(0)

flag=0
print("Program Started")

# To make sure Photo is clicked
photoClicked = False

# List to store EAR ( for Visualisation )
eye_blink_signal=[]

# Alerts Count
earCount=0
marCount=0



while True:
	ret, frame=cap.read()
	frame = imutils.resize(frame, width=600)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	subjects = detect(gray, 0)

	for subject in subjects:
		# Predict the facial landmarks
		shape = predict(gray, subject)

		# Extract the coordinates of the landmarks
		points = []
		for n in range(0, 68):
			x = shape.part(n).x
			y = shape.part(n).y
			points.append((x, y))

		# Convert the points to a NumPy array
		shape = face_utils.shape_to_np(shape)

		# Draw the face mesh using OpenCV
		cv2.polylines(frame, [shape[0:17]], isClosed=False, color=(255, 255, 255), thickness=1)  # Jawline
		cv2.polylines(frame, [shape[17:22]], isClosed=False, color=(255, 255, 255), thickness=1)  # Left eyebrow
		cv2.polylines(frame, [shape[22:27]], isClosed=False, color=(255, 255, 255), thickness=1)  # Right eyebrow
		cv2.polylines(frame, [shape[27:31]], isClosed=False, color=(255, 255, 255), thickness=1)  # Nose bridge
		cv2.polylines(frame, [shape[31:36]], isClosed=False, color=(255, 255, 255), thickness=1)  # Lower nose
		# cv2.polylines(frame, [shape[36:42]], isClosed=True, color=(255, 255, 255), thickness=1)  # Left eye
		# cv2.polylines(frame, [shape[42:48]], isClosed=True, color=(255, 255, 255), thickness=1)  # Right eye
		cv2.polylines(frame, [shape[48:60]], isClosed=True, color=(255, 255, 255), thickness=1)  # Outer lip
		cv2.polylines(frame, [shape[60:68]], isClosed=True, color=(0, 255, 0), thickness=1)  # Inner lip


		# Drawing Eye Contours
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)
		ear = (leftEAR + rightEAR) / 2.0
		
		leftEyeHull = cv2.convexHull(leftEye)							
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

		eye_blink_signal.append(ear)

		mouth = shape[60:68]
		mouthar = mouth_aspect_ratio(mouth)

		cv2.putText(frame, str(f"EAR : {round(ear,2)}"), (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		cv2.putText(frame, str(f"MAR : {round(mouthar,2)}"), (450, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

		# Eye Threshold Check
		if ear <= ethresh:
			
			eye_blink_signal.append(ear)
			
			flag += 1
			if flag >= frame_check:

				cv2.putText(frame, "***********************ALERT!***********************", (10, 30), 
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
				
				# Play Hindi Alarm - Kripya Sadak Pr Dhyaan De
				sound.play()
				time.sleep(1.5)

				if earCount <= 2 :
					sound.play()
					time.sleep(1.5)

				if earCount > 2 and earCount <= 4 :
					alert.play()
					time.sleep(1)
				if earCount == 5:
					alert.stop()
					earCount = 0
					# time.sleep(1)
				earCount += 1
	

				# Photo saving into backend of the driver who is feeling sleepy
				if(photoClicked == False):

					try:
						retval, buffer = cv2.imencode('.jpg', frame)
						image_data = buffer.tobytes()
						SQLStatement = "INSERT INTO Images (Photo) VALUES (?)"
						MyCursor.execute(SQLStatement, (image_data, ))
						MyDB.commit()
						print("Photo Clicked")

						# Sending the SMS
						message = client.messages.create(
							body="The driver has been found drowsy and sleepy while driving. Kindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n",
							from_=Creds.from_number,
							to=Creds.to_number
						)
						print(f"SMS sent successfully! Message SID: {message.sid}")

						photoClicked = True
					except Exception as e:
						print(e)
						print("Photo is not saved into the backend due to some issue")
			
				
		else:
			flag = 0

		# Mouth Threshold Check
		if mouthar >= mthresh:
			if marCount < 4:
				yawn.play()
				time.sleep(1.3)

			if marCount >= 4 :
				alert.play()
				time.sleep(1)
			if marCount == 6:
				alert.stop()
				marCount = 0
				# time.sleep(1)
			marCount += 1

	cv2.imshow("Drowsiness Detection System", frame)

	key = cv2.waitKey(1) & 0xFF

	# Press 'q' to QUIT the program
	if key == ord("q"):
		break

cv2.destroyAllWindows()
cap.release()

# X - axis to plot the graph with EAR with Threshold Value.
xaxis = []
for i in range(0, len(eye_blink_signal)):
 	xaxis.append(0.21)

# Plotting the graph to show the EAR with Threshold Value 
plt.title("Drowsiness Alert")
plt.plot(eye_blink_signal, label = "Eye Aspect Ratio", color = 'r')
plt.plot(xaxis, label = "Threshold Value", color = 'grey')
plt.legend(loc='upper right')
plt.show()


print("Program Ended")
