from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import subprocess
import os
from datetime import datetime
from attendance_tracker import AttendanceTracker

app = Flask(__name__)
CORS(app)

@app.route('/run_live_face_recognition', methods=['POST'])
def run_live_face_recognition():
    try:
        # Run the live_face_recognition_attendance.py script using subprocess
        subprocess.run(['python', 'live_face_recognition_attendance.py'], check=True)
        return jsonify({'status': 'success', 'results': ['Execution completed.']})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'error_message': f'Subprocess error: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'error_message': str(e)})

@app.route('/run_image_face_recognition', methods=['POST'])
def run_image_face_recognition():
    try:
        if 'images[]' not in request.files:
            return jsonify({'status': 'error', 'error_message': 'No image file provided'})

        image_files = request.files.getlist('images[]')

        for i, image_file in enumerate(image_files):
            image_path = f'temp_image_{i}.jpg'  # Unique filename for each image
            image_file.save(image_path)

            # Run face recognition script
            subprocess.run(['python', 'image_face_recognition_attendance.py', image_path], check=True)

            # Remove the temporary image after processing
            os.remove(image_path)

        return jsonify({'status': 'success', 'results': ['Execution completed.']})

    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'error_message': f'Subprocess error: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'error_message': str(e)})

@app.route('/query_attendance', methods=['GET'])
def query_attendance():
    try:
        tracker = AttendanceTracker()

        date = request.args.get('date')
        if not date:
            return jsonify({'status': 'error', 'error_message': 'Missing date parameter'})

        try:
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return jsonify({'status': 'error', 'error_message': 'Invalid date format. Use YYYY-MM-DD.'})

        daily_attendance = tracker.get_daily_attendance(formatted_date)

        if daily_attendance.empty:
            return jsonify({'status': 'success', 'results': ['No Students Found']})

        # Extract unique student names
        unique_names = daily_attendance['Name'].dropna().unique().tolist()

        return jsonify({'status': 'success', 'results': unique_names})

    except Exception as e:
        return jsonify({'status': 'error', 'error_message': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
