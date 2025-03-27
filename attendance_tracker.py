import pandas as pd
import os
from datetime import datetime, timedelta

class AttendanceTracker:
    def __init__(self, csv_file='Attendance.csv'):
        self.csv_file = csv_file
        self.create_csv_if_not_exists()

    def create_csv_if_not_exists(self):
        """
        Create CSV file with default structure if it doesn't exist.
        """
        if not os.path.exists(self.csv_file):
            df = pd.DataFrame(columns=[
                'Name', 
                'Date', 
                'In Time 1', 
                'Out Time 1', 
                'In Time 2', 
                'Out Time 2', 
                'In Time 3', 
                'Out Time 3',
                'Session 1 Duration',
                'Session 2 Duration',
                'Session 3 Duration',
                'Total Hours'
            ])
            # Explicitly set column types
            df = df.astype({
                'Name': 'string',
                'Date': 'string',
                'In Time 1': 'string',
                'Out Time 1': 'string',
                'In Time 2': 'string',
                'Out Time 2': 'string',
                'In Time 3': 'string',
                'Out Time 3': 'string',
                'Session 1 Duration': 'string',
                'Session 2 Duration': 'string',
                'Session 3 Duration': 'string',
                'Total Hours': 'string'
            })
        
            # Save or overwrite the CSV to ensure correct structure
            df.to_csv(self.csv_file, index=False, mode='w')

    def calculate_duration(self, in_time, out_time):
        """
        Calculate duration between in_time and out_time.
        Handles various input types and potential errors.
        """
        # Convert to string and handle NaN or empty values
        in_time = str(in_time).strip() if pd.notna(in_time) else ''
        out_time = str(out_time).strip() if pd.notna(out_time) else ''

        if not in_time or not out_time:
            return timedelta()
        
        try:
            # Try parsing with multiple possible time formats
            formats_to_try = ['%H:%M:%S', '%H:%M']
            
            for time_format in formats_to_try:
                try:
                    in_datetime = datetime.strptime(in_time, time_format)
                    out_datetime = datetime.strptime(out_time, time_format)
                    
                    # Handle cases where out_time might be on the next day
                    if out_datetime < in_datetime:
                        out_datetime += timedelta(days=1)
                    
                    return out_datetime - in_datetime
                except ValueError:
                    continue
            
            # If no format works
            print(f"Error parsing times. In Time: {in_time}, Out Time: {out_time}")
            return timedelta()
        
        except Exception as e:
            print(f"Unexpected error calculating duration: {e}")
            return timedelta()

    def calculate_total_hours(self, df, index):
        """
        Calculate total hours spent in class for a specific record.
        """
        # Calculate individual session durations
        session_durations = []
        total_duration = timedelta()

        for i in range(1, 4):
            in_time = df.loc[index, f'In Time {i}']
            out_time = df.loc[index, f'Out Time {i}']
            
            # Calculate session duration
            session_duration = self.calculate_duration(in_time, out_time)
            
            # Store session duration
            df.loc[index, f'Session {i} Duration'] = str(session_duration)
            
            # Add to total duration if session is complete
            if in_time and out_time:
                total_duration += session_duration
        
        # Store total hours
        df.loc[index, 'Total Hours in Class'] = str(total_duration)
        
        return df

    def mark_attendance(self, name):
        """
        Mark attendance with multiple time entries tracking.
        """
        # Read existing CSV file
        try:
            df = pd.read_csv(self.csv_file, dtype=str)  # Read all columns as strings
        except PermissionError:
            print(f"Permission denied. Cannot access {self.csv_file}. Ensure the file is not open.")
            return
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        # Get current date and time
        now = datetime.now()
        today = now.strftime('%d/%m/%Y')
        current_time = now.strftime('%H:%M:%S')

        # Check if student exists for today
        today_records = df[(df['Name'] == name) & (df['Date'] == today)]

        if today_records.empty:
            # First entry for the day - mark as In Time 1
            new_record = {
                'Name': name,
                'Date': today,
                'In Time 1': current_time,
                'Out Time 1': '',
                'In Time 2': '',
                'Out Time 2': '',
                'In Time 3': '',
                'Out Time 3': '',
                'Session 1 Duration': '',
                'Session 2 Duration': '',
                'Session 3 Duration': '',
                'Total Hours': ''
            }
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            print(f"First attendance entry for {name} at {current_time}")
        else:
            # Student already has an entry for today
            last_record_index = today_records.index[-1]

            # Check which time slot to fill
            time_slots = [
                ('In Time 1', 'Out Time 1'),
                ('In Time 2', 'Out Time 2'),
                ('In Time 3', 'Out Time 3')
            ]

            for in_slot, out_slot in time_slots:
                # If the in-time slot is empty or we find a completely unused record
                if (pd.isna(df.loc[last_record_index, in_slot]) or 
                    df.loc[last_record_index, in_slot] == ''):
                    # Mark the in-time
                    df.loc[last_record_index, in_slot] = current_time
                    print(f"Marked {in_slot} for {name} at {current_time}")
                    break
                
                # If in-time is set but out-time is empty, mark out-time
                elif (pd.notna(df.loc[last_record_index, in_slot]) and 
                      (pd.isna(df.loc[last_record_index, out_slot]) or 
                       df.loc[last_record_index, out_slot] == '')):
                    # Mark out-time
                    df.loc[last_record_index, out_slot] = current_time
                    
                    # Recalculate total hours for this record
                    df = self.calculate_total_hours(df, last_record_index)
                    
                    print(f"Marked {out_slot} for {name} at {current_time}")
                    break

        # Save changes to CSV
        try:
            df.to_csv(self.csv_file, index=False)
        except PermissionError:
            print(f"Permission denied. Cannot save to {self.csv_file}. Ensure the file is not open.")
        except Exception as e:
            print(f"Error saving CSV: {e}")

    def get_daily_attendance(self, date=None):
        """
        Retrieve attendance for a specific date.
        Date should be in 'dd/mm/yyyy' format
        """
        if date is None:
            date = datetime.now().strftime('%d/%m/%Y')

        try:
            df = pd.read_csv(self.csv_file, dtype=str)
            daily_records = df[df['Date'] == date]
            return daily_records
        except Exception as e:
            print(f"Error retrieving daily attendance: {e}")
            return pd.DataFrame()

    def get_student_attendance(self, name):
        """
        Retrieve all attendance records for a specific student.
        """
        try:
            df = pd.read_csv(self.csv_file, dtype=str)
            student_records = df[df['Name'] == name]
            return student_records
        except Exception as e:
            print(f"Error retrieving student attendance: {e}")
            return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    tracker = AttendanceTracker()
    
    # Example of marking attendance multiple times
    tracker.mark_attendance("JOHN DOE")
    # Simulate some time passing
    import time
    time.sleep(2)
    tracker.mark_attendance("JOHN DOE")  # This would mark out time
    
    # Get today's attendance
    today = datetime.now().strftime('%d/%m/%Y')
    print(tracker.get_daily_attendance(today))