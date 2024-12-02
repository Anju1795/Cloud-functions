from google.cloud import secretmanager

def get_push_notification_open_ai_key():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/mentalport-dev/secrets/pushNotificationOpenAiKey/versions/latest"
    response = client.access_secret_version(name=name)
    push_notification_key_value = response.payload.data.decode("UTF-8")
    return push_notification_key_value