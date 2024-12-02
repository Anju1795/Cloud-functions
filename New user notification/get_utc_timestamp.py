from datetime import datetime
import pytz
  
def get_current_utc_timestamp(): 
    current_utc_time = datetime.now(pytz.UTC)
    return current_utc_time