from google.cloud import firestore
import firebase_admin
from firebase_admin import messaging, _messaging_utils
from datetime import datetime

firebase_admin.initialize_app()
client = firestore.Client()

def send_push_notifications(data, context):
    try:
        collection_path, document_path = context.resource.split("/documents/")[1].split("/", 1)
        # Reference to the affected document
        affected_doc = client.document(f"{collection_path}/{document_path}")

        # Get fields from data
        value_fields = data.get('value', {}).get('fields', {})

        # Extract user ID, FCM token, and language
        user_id = document_path.split("/")[0]
        user_fcm_token = get_user_fcm_token(user_id)
        notification_type, notification_content, feature = get_notification_details(affected_doc)
        print(f"The notification type, content, feature is : {notification_type},{notification_content},{feature}")
        #if user_id == 'KUWZxi3iZuMZJTOB5b2x78rdxH13':
        if user_fcm_token and notification_type and notification_content and feature:
            send_user_notification(user_fcm_token, notification_type, notification_content, feature, affected_doc.id)
            # Update the document to set the notification flag
            affected_doc.update({"sendSuccessfully": True})
            affected_doc.update({"sendAt": datetime.now() })

            # Log the notification
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
            print("FCM token not found in user data for:{user_id}.")
    else:
        print("User document not found.")

    # Return None if no token is found or user document doesn't exist
    return None


def get_notification_details(affected_doc):
    user_doc = affected_doc.get()
    if user_doc.exists:
        # Convert user document to a dictionary
        user_data = user_doc.to_dict()

        # Get the notification_type, default to an empty string if not found
        notification_type = user_data.get('notificationType', "")
        notification_content = user_data.get('notificationContent', "")
        feature = user_data.get('feature', "")

        # If notification type is not empty, print and return it
        if notification_type:
            return notification_type, notification_content, feature
        else:
            print("notification_type not found for {user_id}.")
    else:
        print("User document not found.")

    # Return a default
    return "","",""

def send_user_notification(fcmToken, notification_type, notification_content, feature,docId):
    # Todo: confirmation content can be optimized or detailed

    # Define notification content for both English and German
    title = "mentalport coach"
    body = notification_content
    try:
        if notification_type == 'new-user-notification':
            response = messaging.send(messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=fcmToken,
                data={
                    'type': 'newUser'
                }
            ))
        elif notification_type == 'in-user-reminder':
            response = messaging.send(messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=fcmToken,
                data={
                    'type': 'inUseFeature',
                    "notificationDocumentId": docId,
                    "feature": feature
                }
            ))
        elif notification_type == 'recommendation-notification':
            response = messaging.send(messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=fcmToken,
                data={
                    'type': 'recommendation',
                    "notificationDocumentId": docId,
                    "feature": feature
                }
            ))
    except _messaging_utils.UnregisteredError:
        print(f"FCM token for user is unregistered. Token: {fcmToken}")
        # Remove the invalid token from the database
        remove_invalid_fcm_token(fcmToken)

def remove_invalid_fcm_token(fcmToken):
    # Implement your logic to remove the invalid token from your database
    user_docs = client.collection(u'users').where('fcmTokenData.fcmToken', '==', fcmToken).stream()
    for doc in user_docs:
        doc.reference.update({ 'fcmTokenData.fcmToken': None })
        print(f"Removed invalid FCM token from user document")