from google.cloud import firestore
import firebase_admin
from google.cloud import pubsub_v1
from firebase_admin import messaging
from datetime import datetime, timedelta

firebase_admin.initialize_app()
client = firestore.Client()

def send_booking_reminder(data, context):
    try:
        bookings = client.collection('bookings').stream()

        for booking in bookings:
            print("booking id:",booking.id)
            value_fields = booking.to_dict()
            print("value fields:",value_fields)
            timestamp_value = value_fields.get('scheduledDate', {})
            print("scheduledDate:",timestamp_value)
            if timestamp_value:
                timestamp = timestamp_value.timestamp()
                print("scheduled date :",timestamp)
                current_time_value = datetime.now()
                current_time = current_time_value.timestamp()
                print("current time ", current_time)
                time_difference = timestamp - current_time
                print("time diff :", time_difference)

                if 1740 <= time_difference <= 1800:
                    user_id = value_fields.get("userID", {})
                    user_fcm_token = get_user_fcm_token(user_id)
                    user_language = get_user_language(user_id)
                    send_user_notification(user_fcm_token, user_language, booking.id)
                    print("Notification sent to user with ID:", user_id)
    except IndexError as e:
        print("Error:",e)

def get_user_fcm_token(user_id):
    user_doc = client.collection(u'users').document(user_id).get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        fcm_token_data = user_data.get('fcmTokenData', {})
        fcm_token = fcm_token_data.get('fcmToken')

        if fcm_token:
            print(f"User FCM token found: {fcm_token}")
            return fcm_token
        else:
            print("FCM token not found in user data.")
    else:
        print("User document not found.")

    # Return None if no token is found or user document doesn't exist
    return None


def get_user_language(user_id):
    # Retrieve the user document from Firestore
    user_doc = client.collection(u'users').document(user_id).get()

    # Check if the user document exists
    if user_doc.exists:
        # Convert user document to a dictionary
        user_data = user_doc.to_dict()

        # Get the user's language preference, default to an empty string if not found
        user_language = user_data.get('language', "")

        # If user_language is not empty, print and return it
        if user_language:
            print(f"User prefers language: {user_language}")
            return user_language
        else:
            print("Language preference not found.")
    else:
        print("User document not found.")

    # Return a default
    return "de"

def send_user_notification(fcmToken, language, bookingID):
    # Todo: confirmation content can be optimized or detailed

    # Define notification content for both English and German
    confirmation_title_en = "Reminder"
    confirmation_content_en = "Your appointment is scheduled in 30 minutes"
    confirmation_title_de = "Erinnerung"
    confirmation_content_de = "Ihr Termin wird in 30 Minuten vereinbart"
    # Select notification content based on language preference
    if language == "en":
        title = confirmation_title_en
        body = confirmation_content_en
    else:
        title = confirmation_title_de
        body = confirmation_content_de

    # Send the notification
    messaging.send(messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcmToken,
        data={
            'type': 'appointment',
            "title": title,
            "bookingID": bookingID,
            "content": body,
            'appointmentNotificationType': 'appointmentReminder',
        }
    ))
