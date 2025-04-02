import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Authenticate using credentials.json
def authenticate_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
    client = gspread.authorize(creds)
    return client

# Function to log attendance data
def log_attendance_to_sheet(user_name, date, time, latitude, longitude, status):
    try:
        client = authenticate_google_sheets()
        sheet = client.open("AttendanceRecords").sheet1  # Ensure the sheet name is correct

        # Append attendance data
        sheet.append_row([user_name, date, time, latitude, longitude, status])

        print("Attendance logged successfully in Google Sheets.")
        return True
    except Exception as e:
        print(f"Error logging attendance: {e}")
        return False
