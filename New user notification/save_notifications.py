import logging
from get_content_from_openai import get_new_user_notification_content_from_openAi
from get_utc_timestamp import get_current_utc_timestamp
from datetime import datetime, timedelta

def save_notifications(user_id,user_name,language,client,open_ai_key):
    logging.info(f"User name :{user_name}")
    today = datetime.today().date()
    query = client.collection('users').document(user_id) \
        .collection('push_notification_records').where('createdAt', '>=', datetime(today.year, today.month, today.day)) \
        .where('createdAt', '<', datetime(today.year, today.month, today.day) + timedelta(days=1)).limit(1).stream()
    # Query subcollection for the specific user
    is_document_today = any(query)
    if is_document_today:
        # Document with createdAt == today (year-month-day) exists
        print("Document with createdAt equal to today (year-month-day) exists.")
        return
    else:
        print("No document with createdAt == today (year-month-day) exists")
        notification_content = get_new_user_notification_content_from_openAi(user_name,language,open_ai_key)
        if notification_content is None:
            return 
        new_doc_data = {
            'createdAt': get_current_utc_timestamp(),
            'notificationTitle': 'Mentalport',
            'notificationContent': notification_content,
            "sendSuccessfully": False, # this is used to detect if the notification sent via cloud function
            "sendAt":None,  # this will be updated when notification is sent
            "notificationType": "new-user-notification"
        }
        client.collection('users').document(user_id).collection('push_notifications_records').add(new_doc_data)
        print("Notification saved for user")
    return "saving new user notification done"