from datetime import datetime

def is_valid_date(date_str, fmt="%Y-%m-%d"):
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False
