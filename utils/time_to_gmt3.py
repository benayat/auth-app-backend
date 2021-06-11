import pytz
import datetime
def get_local_time(utc_time):
    local_timezone = pytz.timezone("Asia/Jerusalem")
    local_datetime = utc_time.replace(tzinfo=pytz.utc)
    local_datetime = local_datetime.astimezone(local_timezone)
    print(local_datetime)
    return local_datetime

# time_now_here = get_local_time(datetime.datetime.now())
