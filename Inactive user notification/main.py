from google.cloud import firestore
import firebase_admin
from firebase_admin import messaging
from firebase_admin import auth
from datetime import datetime, timedelta
from google.cloud import secretmanager
from openai import OpenAI

firebase_admin.initialize_app()
client = firestore.Client()
secret_client = secretmanager.SecretManagerServiceClient()
name = f"projects/mentalport-dev/secrets/OpenAiKey/versions/latest"
response = secret_client.access_secret_version(name=name)
mentalport_secret_value = response.payload.data.decode("UTF-8")

def daily_reminder_message():
    # Retrieve a list of all users
    #all_users = auth.list_users()
    ## Iterate over all users
    #for user in all_users.iterate_all():
    #    user_uid = user.uid
    users = ['0huTzqszsjT56ALYWJDrDrxF1du1','0MOmKutBXvaW5fqm2lbUNqkgOzm1','18nvUQiwZFfF5hmvKskgqiXCm6T2','563NymlmGTVks6xZomhyG1xBypM2','FkpxsnbsaeX8PCN16qUGAD8TC9v1','KUWZxi3iZuMZJTOB5b2x78rdxH13']
    for user_uid in users:
        print("user:", user_uid)

        last_login = get_last_login_date(user_uid)
        if last_login is not None:
            last_login_timestamp = last_login.timestamp()
            current_time_value = datetime.now()
            current_time = current_time_value.timestamp()
            print("current time ", current_time)
            time_difference = current_time - last_login_timestamp
            print("time diff :", time_difference)
            fifteen_days_seconds = 15 * 24 * 60 * 60
            if time_difference > fifteen_days_seconds:
                user_language = get_user_language(user_uid)
                user_name = get_user_name(user_uid)
                save_notifications(user_uid,user_name,user_language)

def save_notifications(user_id,user_name,language):
    current_year = datetime.now().year
    today = datetime.today().date()
    query = client.collection('users').document(user_id) \
        .collection('daily_recommendation_message').where('createdAt', '>=', datetime(today.year, today.month, today.day)) \
        .where('createdAt', '<', datetime(today.year, today.month, today.day) + timedelta(days=1)).limit(1).stream()
    # Query subcollection for the specific user
    is_document_today = any(query)
    if is_document_today:
        # Document with createdAt == today (year-month-day) exists
        print("Document with createdAt equal to today (year-month-day) exists.")
        return
    else:
        print("No document with createdAt == today (year-month-day) exists")
        new_doc_data = {
            'createdAt': datetime.now(),
            'recommendationMessage': get_notification_content_from_openAi(user_name,language),
        }
    client.collection('users').document(user_id) \
        .collection('daily_recommendation_message').add(new_doc_data)
    print("Notification saved  with ID:", user_id)

def get_notification_content_from_openAi(name,language):
    open_ai_client = OpenAI(api_key=mentalport_secret_value)
    prompt = (
            "A message to remind user " + name + "to use mentalport app."                                                                                              
            "your answer should be like - greet user firstly, then suggest to use the app."
            "you should always use 'we', not 'they."
            "Do not use salutations/regards/blank lines."
            "Please answer in " + language + "."
            "when you're answering in german, capitalize words like Du, Dich, Dein."
    )
    open_ai_response = open_ai_client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    notification_content = ""
    for chunk in open_ai_response:
        if chunk.choices[0].delta.content is not None:
            notification_content += chunk.choices[0].delta.content
    print(notification_content)
    return notification_content

def get_last_login_date(user_uid):
    # Retrieve the user document from Firestore
    user_doc = client.collection(u'users').document(user_uid).get()
    # Check if the user document exists
    if user_doc.exists:
        # Convert user document to a dictionary
        user_data = user_doc.to_dict()
        # Get the user's lastLoginDate, default to an empty string if not found
        lastLoginDate = user_data.get('lastLoginDate', "")
        # If lastLoginDate is not empty, print and return it
        if lastLoginDate:
            print(f"User's last login': {lastLoginDate}")
            return lastLoginDate
        else:
            print("lastLoginDate not found.")
    else:
        print("User document not found.")
        return None
    # Return a default
    return None

def get_user_language(user_uid):
    # Retrieve the user document from Firestore
    user_doc = client.collection(u'users').document(user_uid).get()
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
        return "de"
    # Return a default
    return "de"

def get_user_name(user_uid):
    # Retrieve the user document from Firestore
    user_doc = client.collection(u'users').document(user_uid).get()
    # Check if the user document exists
    if user_doc.exists:
        # Convert user document to a dictionary
        user_data = user_doc.to_dict()
        # Get the user's name, default to an empty string if not found
        user_name = user_data.get('name', "")
        # If user_name is not empty, print and return it
        if user_name:
            print(f"User name: {user_name}")
            return user_name
        else:
            print("User name not found.")
    else:
        print("User document not found.")
        return " "
    # Return a default
    return " "

if __name__ == '__main__':
    daily_reminder_message()