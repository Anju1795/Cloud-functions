import pandas as pd
from datetime import datetime
import pytz

def get_all_users_from_user_docs(user_docs):
    currentDate = datetime.now(pytz.UTC)
    
    all_users = []  # Use a list to collect active user data

    for doc in user_docs:
        doc_data = doc.to_dict()
        last_login_date = doc_data.get('lastLoginDate')
        if last_login_date and isinstance(last_login_date, datetime):  # Ensure it's a datetime object
            try:
                doc_data['userId'] = doc.id 
                doc_data['lastLoginUntilNow'] = (currentDate - last_login_date).days
                all_users.append(doc_data)
            except Exception as e:
                print(f'Error processing date for doc {doc.id}: {e}')
    return pd.DataFrame(all_users)