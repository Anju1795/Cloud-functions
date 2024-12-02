from google.cloud import firestore
import firebase_admin
from firebase_admin import messaging

firebase_admin.initialize_app()
client = firestore.Client()

def coaching_summary_notification(data, context):
    # Extract collection and document path from context
    try:
        collection_path, document_path = context.resource.split("/documents/")[1].split("/", 1)
        # Reference to the affected document
        affected_doc = client.document(f"{collection_path}/{document_path}")

        # Get fields from data
        value_fields = data.get('value', {}).get('fields', {})

        # Extract coach value, coaching summary, user ID, FCM token, and language
        coach_value = value_fields.get('coach', {}).get('stringValue')
        coaching_summary = value_fields.get('finishingReport', {}).get("mapValue")
        user_id = value_fields.get("userID", {}).get("stringValue")
        user_fcm_token = get_user_fcm_token(user_id)
        user_language = get_user_language(user_id)
        prev_summary_value = data.get('oldValue', {}).get('fields', {}).get('finishingReport', {}).get('mapValue')
        prev_coach_value = value_fields.get('__previous', {}).get('fields', {}).get('coach', {}).get('stringValue')

        # Check if zoomLink is already set in the document
        zoom_link = value_fields.get('zoomLink', {}).get('stringValue', "")

        if coach_value != prev_coach_value and coach_value is not None and zoom_link:
            # Check if the notification flag is already set in the document
            notification_sent = value_fields.get('coachConfirmedNotificationSent', {}).get('booleanValue', False)

            if not notification_sent:
                # Send user notification
                send_confirmation_notification(user_fcm_token, user_language, affected_doc.id)

                # Update the document to set the notification flag
                affected_doc.update({"coachConfirmedNotificationSent": True})

                # Log the notification
                print("Notification sent to user with ID:", user_id)


        if coaching_summary is not None and coaching_summary != prev_summary_value:
            send_summary_notification(user_fcm_token, user_language)

            # Log the notification
            print("Notification sent to user with ID:", user_id)

    except IndexError as e:
        print("Error:", e)

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

def send_confirmation_notification(fcmToken, language, bookingID):
    # Todo: confirmation content can be optimized or detailed

    # Define notification content for both English and German
    confirmation_title_en = "Confirmed"
    confirmation_content_en = "Your appointment is confirmed by our coach"
    confirmation_title_de = "Bestätigt"
    confirmation_content_de = "Dein Termin wird von unserem Coach bestätigt"

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
            "bookingID": bookingID,
            "title": title,
            "content": body,
            'appointmentNotificationType': 'appointmentConfirmed',
        }
    ))

def send_summary_notification(fcmToken, language):
    # Todo: confirmation content can be optimized or detailed

    # Define notification content for both English and German
    confirmation_title_en = "Coaching Summary"
    confirmation_content_en = "Summary of your coaching is available now"
    confirmation_title_de = "Coaching Zusammenfassung"
    confirmation_content_de = "Die Zusammenfassung Ihres Coachings ist jetzt verfügbar"

    # Select notification content based on language preference
    if language == "en":
        title = confirmation_title_en
        body = confirmation_content_en
    else:
        title = confirmation_title_de
        body = confirmation_content_de

    # Send the notification
    response = messaging.send(messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcmToken,
        data={
            "title": title,
            "content": body,
            'type': 'appointment',
            'appointmentNotificationType': 'coachingSummary',
        }
    ))
