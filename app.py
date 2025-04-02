from flask import Flask, render_template, request, jsonify
import psutil
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# ------------------- STEP 1: Google Sheets Authentication (Load Once) -------------------
def authenticate_google_sheets():

    credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(credentials_json)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("AttendanceDatabase")
    return sheet.worksheet("Employees"), sheet.worksheet("Sheet1")

employees_sheet, attendance_sheet = authenticate_google_sheets()  # Load once

# ------------------- STEP 2: Get MAC Address -------------------
def get_mac_address():
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:  # MAC address
                    return addr.address.lower()
    except Exception as e:
        return None
    return None

# ------------------- STEP 3: Fetch MAC List from Google Sheets -------------------
def get_registered_mac_addresses():
    try:
        data = employees_sheet.get_all_records()
        return {row["MAC Address"]: row["Name"] for row in data}
    except Exception as e:
        return {}

# ------------------- STEP 4: Get Last Attendance Status (Optimized) -------------------
def get_last_attendance_status(mac_address):
    try:
        records = attendance_sheet.get_all_values()
        for row in reversed(records[-10:]):  # Fetch only last 10 records (reduces API calls)
            if row[1] == mac_address:  # Check MAC address
                return row[3]  # Last status (checked_in/checked_out)
        return "checked_out"  # Default if no record found
    except Exception as e:
        return "checked_out"

# ------------------- STEP 5: Flask Routes -------------------
@app.route("/")
def home():
    mac_address = get_mac_address()
    if not mac_address:
        return "<h1>Error: Unable to retrieve MAC address</h1>", 500

    mac_list = get_registered_mac_addresses()
    if mac_address in mac_list:
        employee_name = mac_list[mac_address]
        last_status = get_last_attendance_status(mac_address)
        return render_template("dashboard.html", name=employee_name, status=last_status)
    else:
        return "<h1>Unauthorized Access</h1>", 403

@app.route('/calendar')
def calendar():
    today = datetime.today()
    return render_template('calendar.html', current_year=today.year, current_month=today.month, current_day=today.day)

@app.route('/leaves')
def leaves():
    return render_template('leaves.html')

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/employee_database')
def employee_database():
    return render_template('employee_database.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ------------------- STEP 6: Mark Attendance in Sheet1 -------------------
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    mac_address = get_mac_address()
    mac_list = get_registered_mac_addresses()

    if mac_address in mac_list:
        employee_name = mac_list[mac_address]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_status = get_last_attendance_status(mac_address)

        new_status = "checked_out" if last_status == "checked_in" else "checked_in"

        try:
            attendance_sheet.append_row([employee_name, mac_address, timestamp, new_status], value_input_option='USER_ENTERED')
            return jsonify({"status": "success", "message": f"You are now {new_status.replace('_', ' ')}", "new_status": new_status})
        except Exception as e:
            return jsonify({"status": "error", "message": "Failed to mark attendance"}), 500
    else:
        return jsonify({"status": "error", "message": "Unauthorized MAC"}), 403

# ------------------- STEP 7: Run Flask App -------------------
if __name__ == "__main__":
    app.run(debug=True)
