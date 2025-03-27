import cv2
import numpy as np
import face_recognition
import os
import pickle
from datetime import datetime
from attendance_tracker import AttendanceTracker

# Initialize the attendance tracker
tracker = AttendanceTracker()

# Path to training images
path = 'Training_images'
encoding_file = 'face_encodings.pkl'  # Cache for face encodings

def load_encodings():
    """Load or generate face encodings."""
    if os.path.exists(encoding_file):
        with open(encoding_file, 'rb') as f:
            classNames, encodeListKnown = pickle.load(f)
        print("Loaded cached encodings.")
    else:
        classNames, encodeListKnown = generate_encodings()
        with open(encoding_file, 'wb') as f:
            pickle.dump((classNames, encodeListKnown), f)
        print("Generated and saved new encodings.")
    return classNames, encodeListKnown

def generate_encodings():
    """Generate face encodings from images."""
    images = []
    classNames = []
    myList = os.listdir(path)
    
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:  # Check if an encoding was found
            encodeList.append(encodings[0])
    
    return classNames, encodeList

def markAttendance(name):
    """Mark attendance using the tracker."""
    tracker.mark_attendance(name)

# Load cached encodings or generate new ones
classNames, encodeListKnown = load_encodings()
print('Encoding Complete')

# Dictionary to track recently recognized faces
recent_recognitions = {}

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
            # Add a delay between recognitions for the same person
            current_time = datetime.now()
            if name not in recent_recognitions or (current_time - recent_recognitions[name]).total_seconds() > 30:
                markAttendance(name)
                recent_recognitions[name] = current_time

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == 27:  # Press 'ESC' to exit
        break

cap.release()
cv2.destroyAllWindows()
