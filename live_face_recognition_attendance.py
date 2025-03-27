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
            try:
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except IndexError:
                print(f"Could not find face encodings in an image. Skipping.")
        return encodeList

    def markAttendance(name):
        tracker.mark_attendance(name)

    # Find encodings for known faces
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    # Dictionary to track recently recognized faces to prevent rapid multiple markings
    recent_recognitions = {}

    # session_attendance = set()

    try:
        # Start video capture
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        
        # Text to explain controls
        # print("\nControls:")
        # print("Press 'r' to reset the current session")
        # print("Press 'q' or ESC to quit the program")

        while True:
            cv2.waitKey(10)

            ret, img = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Resize for processing
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Process faces
            facesCurFrame = face_recognition.face_locations(imgS)
            
            if facesCurFrame:
                encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                # Track authorized and unauthorized faces
                recognized_people = []
                unauthorized_faces = []

                for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                    # Add tolerance to face matching
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.6)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    
                    if len(faceDis) > 0:
                        matchIndex = min(range(len(faceDis)), key=faceDis.__getitem__)

                        # Authorized person (known face)
                        if matches[matchIndex]:
                            name = classNames[matchIndex].upper()
                            recognized_people.append((name, faceLoc))
                            
                            # Mark attendance with time delay - avoid taking same person withing 30 second time delay
                            current_time = datetime.now()
                            if name not in recent_recognitions or (current_time - recent_recognitions[name]).total_seconds() > 30:
                                markAttendance(name)
                                # print(f"Attendance marked for {name}")
                                recent_recognitions[name] = current_time

                            # Mark attendance only once per session
                            # if name not in session_attendance:
                            #     markAttendance(name)
                            #     session_attendance.add(name)
                            # print(f"Attendance marked for {name}")
                        
                        # Unauthorized person (unknown face)
                        else:
                            unauthorized_faces.append(faceLoc)

                # Draw rectangles for recognized people (green)
                for name, faceLoc in recognized_people:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                
                # Draw rectangles for unauthorized people (red)
                for faceLoc in unauthorized_faces:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(img, 'UNKNOWN', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Add text to show current session status
            # cv2.putText(img, f"Marked: {', '.join(session_attendance) if session_attendance else 'None'}", 
            #             (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Webcam', img)

            # Exit conditions
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # ESC or 'q' key
                break

            # Exit and reset conditions
            # key = cv2.waitKey(1) & 0xFF
            # if key == 27 or key == ord('q'):  # ESC or 'q' key
            #     break
            # elif key == ord('r'):  # 'r' key to reset session
            #     session_attendance.clear()
            #     print("\nSession reset. Ready to mark new attendances.")

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


# Performance increased Implementation
# import cv2
# import face_recognition
# import os
# from datetime import datetime
# import numpy as np
# import sys
# import threading

# from attendance_tracker import AttendanceTracker

# def run_face_recognition():
#     # Performance optimization: Initialize only once
#     tracker = AttendanceTracker()

#     # Preload and encode images more efficiently
#     def load_known_faces(path):
#         known_faces = []
#         known_names = []
#         for filename in os.listdir(path):
#             # Only process image files
#             if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
#                 img_path = os.path.join(path, filename)
#                 img = face_recognition.load_image_file(img_path)
                
#                 # Find face encodings more efficiently
#                 face_encodings = face_recognition.face_encodings(img)
#                 if face_encodings:
#                     known_faces.append(face_encodings[0])
#                     known_names.append(os.path.splitext(filename)[0].upper())
#                 else:
#                     print(f"No face found in {filename}")
        
#         return known_faces, known_names

#     # Efficient face loading
#     path = 'Training_images'
#     known_face_encodings, known_names = load_known_faces(path)
#     print(f'Loaded {len(known_names)} known faces')

#     # Optimize video capture
#     def optimize_camera_settings(cap):
#         # Set camera properties for faster processing
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#         cap.set(cv2.CAP_PROP_FPS, 30)
#         cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

#     # Efficient face recognition function
#     def recognize_faces(frame, known_face_encodings, known_names):
#         # Smaller resize for faster processing
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         rgb_small_frame = small_frame[:, :, ::-1]  # Convert BGR to RGB
        
#         # Find faces more efficiently
#         face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
#         recognized_people = []
#         unauthorized_faces = []

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # More efficient face matching
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            
#             # Find best match
#             if True in matches:
#                 best_match_index = matches.index(True)
#                 name = known_names[best_match_index]
#                 recognized_people.append((name, (top, right, bottom, left)))
#             else:
#                 unauthorized_faces.append((top, right, bottom, left))
        
#         return recognized_people, unauthorized_faces

#     # Main recognition loop
#     def run_recognition():
#         # Improve camera initialization
#         cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Direct Show for faster Windows camera access
#         optimize_camera_settings(cap)

#         # Track attendance marking for the current session
#         session_attendance = set()

#         try:
#             while True:
#                 # More efficient frame reading
#                 ret, frame = cap.read()
#                 if not ret:
#                     break

#                 # Efficient face recognition
#                 recognized_people, unauthorized_faces = recognize_faces(
#                     frame, known_face_encodings, known_names
#                 )

#                 # Attendance marking and visualization
#                 for name, (top, right, bottom, left) in recognized_people:
#                     if name not in session_attendance:
#                         tracker.mark_attendance(name)
#                         session_attendance.add(name)
#                         print(f"Attendance marked for {name}")

#                     # Scale locations back to original frame
#                     top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
                    
#                     # Draw rectangles and names
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#                     cv2.putText(frame, name, (left + 6, bottom - 6), 
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

#                 # Draw unauthorized faces
#                 for top, right, bottom, left in unauthorized_faces:
#                     top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#                     cv2.putText(frame, 'UNKNOWN', (left + 6, bottom - 6), 
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

#                 # Display frame
#                 cv2.imshow('Attendance System', frame)

#                 # Exit conditions
#                 key = cv2.waitKey(1) & 0xFF
#                 if key in [27, ord('q')]:  # ESC or 'q'
#                     break
#                 elif key == ord('r'):  # Reset session
#                     session_attendance.clear()
#                     print("Session reset. Ready for new attendances.")

#         except Exception as e:
#             print(f"Error in recognition: {e}")
#         finally:
#             cap.release()
#             cv2.destroyAllWindows()

#     # Start recognition
#     run_recognition()

# if __name__ == "__main__":
#     run_face_recognition()


# Another method

# import cv2
# import face_recognition
# import os
# from datetime import datetime
# import numpy as np
# import sys

# from attendance_tracker import AttendanceTracker

# def run_face_recognition():
#     # Initialize the attendance tracker
#     tracker = AttendanceTracker()

#     path = 'Training_images'
#     images = []
#     classNames = []
#     myList = os.listdir(path)
#     print(myList)
#     for cl in myList:
#         curImg = cv2.imread(f'{path}/{cl}')
#         images.append(curImg)
#         classNames.append(os.path.splitext(cl)[0])
#     print(classNames)

#     def findEncodings(images):
#         encodeList = []
#         for img in images:
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             # Add error handling for face encodings
#             try:
#                 encode = face_recognition.face_encodings(img)[0]
#                 encodeList.append(encode)
#             except IndexError:
#                 print(f"Could not find face encodings in an image. Skipping.")
#         return encodeList

#     def markAttendance(name):
#         # Use the new attendance tracker method
#         tracker.mark_attendance(name)

#     # Find encodings for known faces
#     encodeListKnown = findEncodings(images)
#     print('Encoding Complete')

#     # Dictionary to track recently recognized faces to prevent rapid multiple markings
#     recent_recognitions = {}

#     try:
#         # Start video capture
#         cap = cv2.VideoCapture(0)

#         # Check if camera opened successfully
#         if not cap.isOpened():
#             print("Error: Could not open camera.")
#             return

#         while True:
#             # Add a small delay to reduce CPU usage
#             cv2.waitKey(10)

#             # Capture frame-by-frame with error handling
#             ret, img = cap.read()
#             if not ret:
#                 print("Failed to grab frame")
#                 break

#             # Reduce processing frequency and size
#             imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
#             imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

#             # Process faces less frequently
#             facesCurFrame = face_recognition.face_locations(imgS)
            
#             # Only process if faces are detected
#             if facesCurFrame:
#                 encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

#                 for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
#                     # Add a tolerance to face matching to reduce false positives
#                     matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.6)
#                     faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    
#                     if len(faceDis) > 0:
#                         matchIndex = min(range(len(faceDis)), key=faceDis.__getitem__)

#                         if matches[matchIndex]:
#                             name = classNames[matchIndex].upper()
#                             y1, x2, y2, x1 = faceLoc
#                             y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#                             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                             cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#                             cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                            
#                             # Add a delay between recognitions for the same person
#                             current_time = datetime.now()
#                             if name not in recent_recognitions or (current_time - recent_recognitions[name]).total_seconds() > 30:
#                                 markAttendance(name)
#                                 recent_recognitions[name] = current_time

#             cv2.imshow('Webcam', img)

#             # Exit conditions
#             key = cv2.waitKey(1) & 0xFF
#             if key == 27 or key == ord('q'):  # ESC or 'q' key
#                 break

#     except KeyboardInterrupt:
#         print("\nFace recognition interrupted by user.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Ensure resources are released
#         if 'cap' in locals():
#             cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     run_face_recognition()