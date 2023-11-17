
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv


load_dotenv()

email_address = os.getenv('EMAIL_ADDRESS')
email_password = os.getenv('EMAIL_PASSWORD')
to_email = input('Enter Recipient Email :  ')

def send_message(email_address, email_password, to_email, subject, body, sleep_image_data=None, yawn_image_data=None):
	message = MIMEMultipart()
	message['From'] = email_address
	message['To'] = to_email
	message['Subject'] = subject
	message.attach(MIMEText(body, 'plain'))
	if sleep_image_data:
		image_attachment = MIMEImage(sleep_image_data, name='sleepy_image.jpg')
		message.attach(image_attachment)
	if yawn_image_data:
		image_attachment = MIMEImage(sleep_image_data, name='yawn_image.jpg')
		message.attach(image_attachment)

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email_address, email_password)
	server.sendmail(email_address, to_email, message.as_string())

def get_user_id(email):
    MyCursor.execute("SELECT id FROM Users WHERE Email = ?", (email,))
    user_id = MyCursor.fetchone()
    if user_id:
        return user_id[0]
    else:
        MyCursor.execute("INSERT INTO Users (Email) VALUES (?)", (email,))
        MyDB.commit()
        return MyCursor.lastrowid


# Initialising Database to store Images
MyDB = sqlite3.connect('Drowsy.db')
MyCursor=MyDB.cursor()


# MyCursor.execute("CREATE TABLE IF NOT EXISTS Images (id INTEGER PRIMARY KEY AUTOINCREMENT, Photo BLOB NOT NULL)")
MyCursor.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT UNIQUE NOT NULL)")
MyCursor.execute("CREATE TABLE IF NOT EXISTS Images_Data (id INTEGER PRIMARY KEY AUTOINCREMENT, UserId INTEGER, Photo BLOB NOT NULL, FOREIGN KEY(UserId) REFERENCES Users(id))")


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

# Driver's Mouth Aspect Ratio
def mouth_aspect_ratio(mouth):
	A = distance.euclidean(mouth[1], mouth[7])
	B = distance.euclidean(mouth[3], mouth[5])
	C = distance.euclidean(mouth[0], mouth[4])
	mar = (A + B) / (2.0 * C)
	return mar

# EAR Threshold Value
ethresh = 0.22
# MAR Threshold Value
mthresh = 0.6
# Check after every frame_check frames
frame_check = 20




detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")      # Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"] #[36, 37, 38, 39, 40, 41]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]#[42, 43, 44, 45, 46, 47]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["inner_mouth"]#[60, 61, 62, 63, 64, 65, 66, 67, 68]


# Live Camera Frame Capture
cap=cv2.VideoCapture(0)

flag=0
print("Program Started")

# To make sure Photo is clicked
photoClicked = False
mouthPhotoClicked = False

# Photo Sent To Mail or Not
sleepPhoto = False
yawnPhoto = False


# List to store EAR ( for Visualisation )
eye_blink_signal=[]
# List to store MAR ( for Visualisation )
mouth_yawn_signal=[]

# Alerts Count
earCount=0
marCount=0

# If Found Sleepy or Yawning
sleep_image_data = False
yawn_image_data = False


while True:
	ret, frame=cap.read()
	frame = imutils.resize(frame, width=600)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	subjects = detect(gray, 0)
	frame_copy = frame.copy()
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
		mouth_yawn_signal.append(mouthar)
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
					user_id = get_user_id(to_email)
					try:
						

						retval, buffer = cv2.imencode('.jpg', frame_copy)
						sleep_image_data = buffer.tobytes()
						SQLStatement = "INSERT INTO Images_Data (UserId, Photo) VALUES (?, ?)"
						MyCursor.execute(SQLStatement, (user_id, sleep_image_data))
						MyDB.commit()
						print("Photo Clicked")


						sleepPhoto = True




						# try:
						# 	subject = "Driver Drowsiness Alert"
						# 	body = "The driver has been found drowsy and sleepy while driving. Checkout the image in attachments. \nKindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n"
						# 	send_message(email_address, email_password, to_email, subject, body, sleep_image_data)
						# 	print('Message Sent Successfully...')
						# except:
						# 	print('Recipient Not Found...')

						photoClicked = True
					except Exception as e:
						print(e)
						print("Photo is not saved into the backend due to some issue")
			
				
		else:
			flag = 0

		# Mouth Threshold Check
		if mouthar >= mthresh:

			mouth_yawn_signal.append(mouthar)

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

			# Photo saving into backend of the driver who is feeling sleepy
			if(mouthPhotoClicked == False):
				user_id = get_user_id(to_email)
				try:

					retval, buffer = cv2.imencode('.jpg', frame_copy)
					yawn_image_data = buffer.tobytes()
					SQLStatement = "INSERT INTO Images_Data (UserId, Photo) VALUES (?, ?)"
					MyCursor.execute(SQLStatement, (user_id, yawn_image_data))
					MyDB.commit()
					print("Photo Clicked")

					yawnPhoto = True
					
					# try:
					# 	subject = "Driver Drowsiness Alert"
					# 	body = "The driver has been found drowsy and sleepy while driving. Checkout the image in attachments. \nKindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n"
					# 	send_message(email_address, email_password, to_email, subject, body, yawn_image_data)
					# 	print('Message Sent Successfully...')
					# except:
					# 	print('Recipient Not Found...')

					mouthPhotoClicked = True
				except Exception as e:
					print(e)
					print("Photo is not saved into the backend due to some issue")

	cv2.imshow("Drowsiness Detection System", frame)

	key = cv2.waitKey(1) & 0xFF

	# Press 'q' to QUIT the program
	if key == ord("q"):
		break

if sleep_image_data and yawn_image_data:
	if sleepPhoto == True and yawnPhoto == True:
		try:
			subject = "Driver Drowsiness Alert"
			body = "The driver has been found Drowsy and Sleepy while driving. Checkout the image in attachments. \nKindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n"
			send_message(email_address, email_password, to_email, subject, body, sleep_image_data=sleep_image_data, yawn_image_data=yawn_image_data)
			print('Message Sent Successfully...')
		except:
			print('Recipient Not Found...')
if sleep_image_data and not yawn_image_data:
	if sleepPhoto == True:
		try:
			subject = "Driver Drowsiness Alert"
			body = "The driver has been found Sleepy while driving. Checkout the image in attachments. \nKindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n"
			send_message(email_address, email_password, to_email, subject, body, sleep_image_data=sleep_image_data)
			print('Message Sent Successfully...')
		except:
			print('Recipient Not Found...')
if yawn_image_data and not sleep_image_data:
	if yawnPhoto == True:
		try:
			subject = "Driver Drowsiness Alert"
			body = "The driver has been found Yawning while driving. Checkout the image in attachments. \nKindly Contact the driver ASAP. \n\nRegards, \nDriver's Drowsiness Detector\n"
			send_message(email_address, email_password, to_email, subject, body, yawn_image_data=yawn_image_data)
			print('Message Sent Successfully...')
		except:
			print('Recipient Not Found...')

cv2.destroyAllWindows()
cap.release()


# X - axis to plot the graph with EAR, MAR, and Yawn threshold values.
xaxis_ear = [0.22] * len(eye_blink_signal)
xaxis_mar = [0.6] * len(mouth_yawn_signal)
xaxis_yawn = [mouthar] * len(mouth_yawn_signal)  # Provide the actual yawn threshold value

# Plotting the graph to show the EAR, MAR, and Yawn with Threshold Values
plt.title("Drowsiness Alert")
plt.plot(eye_blink_signal, label="Eye Aspect Ratio", color='r')
plt.plot(xaxis_ear, label="EAR Threshold", color='grey', linestyle='--')

plt.plot(mouth_yawn_signal, label="Mouth Aspect Ratio", color='g')
plt.plot(xaxis_mar, label="MAR Threshold", color='blue', linestyle='--')

plt.legend(loc='upper right')
plt.show()

print("Program Ended")
