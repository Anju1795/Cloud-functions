from google.cloud import firestore
import firebase_admin
from firebase_admin import messaging

firebase_admin.initialize_app()
client = firestore.Client()

def coach_suggestions_notification(data, context):
    # Extract collection and document path from context
    try:
        collection_path, document_path = context.resource.split("/documents/")[1].split("/", 1)
        # Reference to the affected document
        affected_doc = client.document(f"{collection_path}/{document_path}")

        # Get fields from data
        value_fields = data.get('value', {}).get('fields', {})

        # Extract user ID, FCM token, and language
        user_id = document_path.split("/")[0]
        user_fcm_token = get_user_fcm_token(user_id)
        user_language = get_user_language(user_id)

        send_user_notification(user_fcm_token, user_language)

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


def send_user_notification(fcmToken, language):
    # Todo: confirmation content can be optimized or detailed

    # Define notification content for both English and German
    confirmation_title_en = "Coach Suggestions"
    confirmation_content_en = "Suggestions are available from your coach"
    confirmation_title_de = "Coach-Vorschläge"
    confirmation_content_de = "Vorschläge erhalten Sie von Ihrem Coach"

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
        data={ 'type': 'coachSuggestions',
               "title": title,
               "content": body}
    ))





