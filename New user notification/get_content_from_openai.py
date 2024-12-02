
from get_response_from_open_ai import get_response_from_openAi


def get_new_user_notification_content_from_openAi(name,language,openai_api_key):
    name = str(name)
    language = str(language)
    prompt = "say something to remind the new user " + name
    prompt += "to use the app in one sentence, using language "
    if language == "en":
        prompt += "English"
    else:
        prompt += "German"

    prompt_for_cloud_function = {
        "messages": [
            {"role": "user", "content": prompt},
        ]
    }
    response = get_response_from_openAi(openai_api_key,prompt_for_cloud_function)
    return response