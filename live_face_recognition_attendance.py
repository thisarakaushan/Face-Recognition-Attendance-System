import cv2
import face_recognition
import os
from datetime import datetime
import numpy as np
import sys

from attendance_tracker import AttendanceTracker

def run_face_recognition():
    # Initialize the attendance tracker
    tracker = AttendanceTracker()

    path = 'Training_images'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Add error handling for face encodings
            try:
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except IndexError:
                print(f"Could not find face encodings in an image. Skipping.")
        return encodeList

    def markAttendance(name):
        # Use the new attendance tracker method
        tracker.mark_attendance(name)

    # Find encodings for known faces
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    # Dictionary to track recently recognized faces to prevent rapid multiple markings
    recent_recognitions = {}

    try:
        # Start video capture
        cap = cv2.VideoCapture(0)

        # Check if camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            # Add a small delay to reduce CPU usage
            cv2.waitKey(10)

            # Capture frame-by-frame with error handling
            ret, img = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Reduce processing frequency and size
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Process faces less frequently
            facesCurFrame = face_recognition.face_locations(imgS)
            
            # Only process if faces are detected
            if facesCurFrame:
                encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                    # Add a tolerance to face matching to reduce false positives
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.6)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    
                    if len(faceDis) > 0:
                        matchIndex = min(range(len(faceDis)), key=faceDis.__getitem__)

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

            # Exit conditions
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # ESC or 'q' key
                break

    except KeyboardInterrupt:
        print("\nFace recognition interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure resources are released
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_recognition()

# import cv2
# import face_recognition
# import os
# from datetime import datetime
# from attendance_tracker import AttendanceTracker

# # Initialize the attendance tracker
# tracker = AttendanceTracker()

# path = 'Training_images'
# images = []
# classNames = []
# myList = os.listdir(path)
# print(myList)
# for cl in myList:
#     curImg = cv2.imread(f'{path}/{cl}')
#     images.append(curImg)
#     classNames.append(os.path.splitext(cl)[0])
# print(classNames)

# def findEncodings(images):
#     encodeList = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
#     return encodeList

# def markAttendance(name):
#     # Use the new attendance tracker method
#     tracker.mark_attendance(name)

# # Find encodings for known faces
# encodeListKnown = findEncodings(images)
# print('Encoding Complete')

# # Start video capture
# cap = cv2.VideoCapture(0)

# # Dictionary to track recently recognized faces to prevent rapid multiple markings
# recent_recognitions = {}

# while True:
#     success, img = cap.read()
#     imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
#     imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

#     facesCurFrame = face_recognition.face_locations(imgS)
#     encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

#     for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
#         matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
#         faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
#         matchIndex = min(range(len(faceDis)), key=faceDis.__getitem__)

#         if matches[matchIndex]:
#             name = classNames[matchIndex].upper()
#             y1, x2, y2, x1 = faceLoc
#             y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
#             # Add a delay between recognitions for the same person
#             current_time = datetime.now()
#             if name not in recent_recognitions or (current_time - recent_recognitions[name]).total_seconds() > 30:
#                 markAttendance(name)
#                 recent_recognitions[name] = current_time

#     cv2.imshow('Webcam', img)
#     if cv2.waitKey(1) == 27: 
#         break

# cap.release()
# cv2.destroyAllWindows()