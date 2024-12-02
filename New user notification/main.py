import logging
from firebase_admin import auth
from datetime import datetime
import pytz
from check_day_since_creation import check_day_since_creation
from get_all_users import get_all_users_from_user_docs
from get_push_notification_open_ai_key import get_push_notification_open_ai_key
from google.cloud import firestore
import firebase_admin

firebase_admin.initialize_app()
client = firestore.Client()
open_ai_key = get_push_notification_open_ai_key()


def saveNotificationForNewUsers():
    print("function starts")
    all_users = get_all_users(client)
    save_new_user_notification(all_users)


def save_new_user_notification(all_users):
    #get the user list from authentication
    users_list = auth.list_users()
    # Iterate over all users
    for user in users_list.iterate_all():
        user_uid = user.uid
        user_creation_time= user.user_metadata.creation_timestamp / 1000.0
        user_creation_time = datetime.fromtimestamp(user_creation_time, pytz.UTC)
        print(f"user:{user_uid}")
        print(f"Time: {user_creation_time}")
        currentDate = datetime.now(pytz.UTC)
        # Calculate the number of days since user creation
        days_since_creation = (currentDate - user_creation_time).days
        print(f"days_since_creation: {days_since_creation}")
        # Send reminders based on the number of days since user creation
        check_day_since_creation(all_users,days_since_creation,user_uid,client,open_ai_key)
    return "Writting notification document for new user is done"

def get_all_users(db):
    return get_all_users_from_user_docs(db.collection(u'users').stream())

