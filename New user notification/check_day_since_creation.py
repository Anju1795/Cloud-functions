import logging
from save_notifications import save_notifications
from get_user_info import get_user_info

logging.basicConfig(level=logging.INFO)
def check_day_since_creation(users,days,id,client,open_ai_key):
    #logging.info(f"Checking user {id} with {days} days since creation.")
    if days <= 14:
        print(f"User {id} within 14 days.")
        user_name, user_language = get_user_info(users, id)
        save_notifications(id,user_name,user_language,client,open_ai_key)
    elif 14 < days <= 30 and days % 2 == 1:
        print(f"User {id} 14-30 days.")
        user_name, user_language = get_user_info(users, id)
        save_notifications(id,user_name,user_language,client,open_ai_key)
    elif 30 < days <= 60 and days % 7 == 0:
        print(f"User {id} 30-60 days.")
        user_name, user_language = get_user_info(users, id)
        save_notifications(id,user_name,user_language,client,open_ai_key)
    else:
        print(f"{id} Old User.")
    return "checking done"
