def test_google_sheets():
    try:
        mac_list = [mac.strip().lower().replace("-", ":") for mac in employees_sheet.col_values(3)]
        print("MAC Addresses from Google Sheets:", mac_list)
    except Exception as e:
        print("Google Sheets Error:", e)

test_google_sheets()