import cv2
import face_recognition
import os
import sys
import numpy as np
from attendance_tracker import AttendanceTracker

class face_recognition_system:
    def __init__(self, training_images_path='Training_images', confidence_threshold=0.6):
        """
        Initialize the attendance system with known face encodings
        
        Args:
            training_images_path (str): Path to directory containing known face images
            confidence_threshold (float): Threshold for face recognition confidence
        """
        self.tracker = AttendanceTracker()
        self.training_images_path = training_images_path
        self.confidence_threshold = confidence_threshold
        
        # Load known images and their encodings
        self.known_images = []
        self.known_class_names = []
        self.known_encodings = self.load_known_faces()

    def load_known_faces(self):
        """
        Load known face images and generate their encodings
        
        Returns:
            list: Face encodings for known individuals
        """
        for cl in os.listdir(self.training_images_path):
            cur_img = cv2.imread(os.path.join(self.training_images_path, cl))
            self.known_images.append(cur_img)
            # Use filename (without extension) as name
            self.known_class_names.append(os.path.splitext(cl)[0])
        
        return self.find_encodings(self.known_images)

    def find_encodings(self, images):
        """
        Generate face encodings for a list of images
        
        Args:
            images (list): List of images to encode
        
        Returns:
            list: Face encodings for the images
        """
        encode_list = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Handle cases where no face is detected
            face_encodings = face_recognition.face_encodings(img)
            if face_encodings:
                encode_list.append(face_encodings[0])
        return encode_list

    def recognize_faces_in_image(self, image_path):
        """
        Recognize faces in a single image and mark attendance
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            tuple: Processed image and list of recognized names and unknown faces
        """
        # Read the image
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect faces in the image
        faces_cur_frame = face_recognition.face_locations(img_rgb)
        encodes_cur_frame = face_recognition.face_encodings(img_rgb, faces_cur_frame)

        recognized_names = []
        unknown_faces = []

        # Process each detected face
        for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
            # Compare face with known encodings
            matches = face_recognition.compare_faces(self.known_encodings, encode_face)
            face_dis = face_recognition.face_distance(self.known_encodings, encode_face)
            
            # Find the best match
            if len(face_dis) > 0:
                match_index = min(range(len(face_dis)), key=face_dis.__getitem__)

                if matches[match_index] and face_dis[match_index] < self.confidence_threshold:
                    name = self.known_class_names[match_index].upper()
                    
                    # Draw bounding box and name
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    # Mark attendance
                    self.tracker.mark_attendance(name)
                    recognized_names.append(name)
                else:
                    # Unknown face
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, "UNKNOWN", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    # Store unknown face location
                    unknown_faces.append({
                        'location': (x1, y1, x2, y2),
                        'encoding': encode_face
                    })

        return img, recognized_names, unknown_faces

    def process_multiple_images(self, image_paths):
        """
        Process multiple images and mark attendance for each
        
        Args:
            image_paths (list): List of image file paths
        
        Returns:
            dict: Dictionary of image paths and recognized names
        """
        results = {}
        for image_path in image_paths:
            processed_img, names, unknown_faces = self.recognize_faces_in_image(image_path)
            
            # Save the processed image (optional)
            output_filename = f'output_{os.path.basename(image_path)}'
            cv2.imwrite(output_filename, processed_img)
            
            results[image_path] = {
                'recognized_names': names,
                'unknown_faces_count': len(unknown_faces),
                'output_image': output_filename
            }
            
            # Display the processed image
            cv2.imshow(f'Recognized Faces - {os.path.basename(image_path)}', processed_img)
        
        # Wait for a key press after all images are processed
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return results

def main():
    # Check if image paths are provided
    if len(sys.argv) < 2:
        print("Usage: python advanced_face_recognition.py <image1_path> <image2_path> ...")
        sys.exit(1)
    
    # Get image paths from command line arguments
    image_paths = sys.argv[1:]
    
    # Initialize the attendance system
    attendance_system = face_recognition_system()
    
    # Process multiple images
    results = attendance_system.process_multiple_images(image_paths)
    
    # Print results
    print("\nAttendance Results:")
    for image_path, data in results.items():
        print(f"\nImage: {image_path}")
        print(f"Recognized Names: {', '.join(data['recognized_names']) if data['recognized_names'] else 'None'}")
        print(f"Unknown Faces: {data['unknown_faces_count']}")
        print(f"Output Image: {data['output_image']}")

if __name__ == "__main__":
    main()

# import cv2
# import face_recognition
# import os
# from datetime import datetime
# import sys
# from attendance_tracker import AttendanceTracker

# # Initialize the attendance tracker
# tracker = AttendanceTracker()

# def find_encodings(images):
#     encode_list = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encode_list.append(encode)
#     return encode_list

# def mark_attendance(name):
#     # Use the new attendance tracker method
#     tracker.mark_attendance(name)

# def recognize_faces(image_path, known_encodings, known_names):
#     img = cv2.imread(image_path)
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#     faces_cur_frame = face_recognition.face_locations(img_rgb)
#     encodes_cur_frame = face_recognition.face_encodings(img_rgb, faces_cur_frame)

#     for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
#         matches = face_recognition.compare_faces(known_encodings, encode_face)
#         face_dis = face_recognition.face_distance(known_encodings, encode_face)
#         match_index = min(range(len(face_dis)), key=face_dis.__getitem__)

#         if matches[match_index]:
#             name = known_names[match_index].upper()
#             y1, x2, y2, x1 = face_loc
#             y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
#             mark_attendance(name)

#     cv2.imshow('Recognized Faces', img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python image_face_recognition_attendance.py <image_path>")
#         sys.exit(1)

#     image_path = sys.argv[1]

#     path = 'Training_images'

#     # Load known images and their encodings
#     known_images = []
#     known_class_names = []

#     for cl in os.listdir(path):
#         cur_img = cv2.imread(f'{path}/{cl}')
#         known_images.append(cur_img)
#         known_class_names.append(os.path.splitext(cl)[0])

#     known_encodings = find_encodings(known_images)

#     # Process the specified image
#     recognize_faces(image_path, known_encodings, known_class_names)