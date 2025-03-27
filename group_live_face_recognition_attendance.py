import cv2
import face_recognition
import numpy as np
from typing import List, Tuple

class GroupRecognition:
    def __init__(self, known_encodings: List, known_names: List[str]):
        """
        Initialize group recognition system
        
        :param known_encodings: List of face encodings for known people
        :param known_names: List of names corresponding to known encodings
        """
        self.known_encodings = known_encodings
        self.known_names = known_names

    def process_group(self, frame: np.ndarray) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Process group in the frame
        
        :param frame: Input video frame
        :return: Processed frame, list of recognized names, list of unauthorized names
        """
        # Resize frame for faster processing
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Detect faces
        faces_cur_frame = face_recognition.face_locations(imgS)
        encodes_cur_frame = face_recognition.face_encodings(imgS, faces_cur_frame)

        recognized_names = []
        unauthorized_names = []

        # Process each detected face
        for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
            # Compare face with known faces
            matches = face_recognition.compare_faces(
                self.known_encodings, 
                encode_face, 
                tolerance=0.6
            )
            face_distances = face_recognition.face_distance(self.known_encodings, encode_face)

            # Find best match
            if len(face_distances) > 0:
                match_index = min(range(len(face_distances)), key=face_distances.__getitem__)

                if matches[match_index]:
                    # Recognized face
                    name = self.known_names[match_index].upper()
                    recognized_names.append(name)
                    
                    # Draw green rectangle for recognized face
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                else:
                    # Unauthorized face
                    unauthorized_names.append('UNKNOWN')
                    
                    # Draw red rectangle for unauthorized face
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, 'UNKNOWN', (x1 + 6, y2 - 6), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        return frame, recognized_names, unauthorized_names
    


# Code for live_face_recognition_attendance.py

# import cv2
# import face_recognition
# import os
# from datetime import datetime
# import numpy as np
# import sys

# from attendance_tracker import AttendanceTracker
# from group_recognition import GroupRecognition

# def findEncodings(images):
#     """
#     Find face encodings for given images
    
#     :param images: List of images to encode
#     :return: List of face encodings
#     """
#     encodeList = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         try:
#             encode = face_recognition.face_encodings(img)[0]
#             encodeList.append(encode)
#         except IndexError:
#             print(f"Could not find face encodings in an image. Skipping.")
#     return encodeList

# def run_face_recognition():
#     # Initialize the attendance tracker
#     tracker = AttendanceTracker()

#     # Path to training images
#     path = 'Training_images'
    
#     # Load images
#     images = []
#     classNames = []
#     myList = os.listdir(path)
    
#     for cl in myList:
#         curImg = cv2.imread(f'{path}/{cl}')
#         images.append(curImg)
#         classNames.append(os.path.splitext(cl)[0])
    
#     # Find encodings for known faces
#     encodeListKnown = findEncodings(images)
    
#     # Create group recognition instance
#     group_rec = GroupRecognition(encodeListKnown, classNames)
    
#     # Dictionary to track recently recognized faces
#     recent_recognitions = {}

#     try:
#         # Start video capture
#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():
#             print("Error: Could not open camera.")
#             return

#         while True:
#             # Small delay to reduce CPU usage
#             cv2.waitKey(10)

#             # Capture frame
#             ret, frame = cap.read()
#             if not ret:
#                 print("Failed to grab frame")
#                 break

#             # Process group recognition
#             processed_frame, recognized_names, unauthorized_names = group_rec.process_group(frame)

#             # Mark attendance for recognized faces
#             current_time = datetime.now()
#             for name in recognized_names:
#                 if name not in recent_recognitions or (current_time - recent_recognitions[name]).total_seconds() > 30:
#                     tracker.mark_attendance(name)
#                     recent_recognitions[name] = current_time

#             # Display the frame
#             cv2.imshow('Webcam', processed_frame)

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
#         cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     run_face_recognition()