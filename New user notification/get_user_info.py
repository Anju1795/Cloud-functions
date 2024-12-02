def get_user_info(all_users, user_id):
    user_info = all_users[all_users['userId'] == user_id]
    if len(user_info) == 0:
        # Handle case where user_id is not found
        return "User", "de"
    user_name = user_info.iloc[0]['name']
    user_language = user_info.iloc[0]['language']
    return user_name, user_language