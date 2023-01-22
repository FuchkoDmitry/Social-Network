import requests
from core.email_conf import email_check_api_key


def valid_mail(email_to_check: str):
    url = 'https://emailvalidation.abstractapi.com/v1/'
    params = {'api_key': email_check_api_key, "email": email_to_check}
    response = requests.get(url, params=params)
    if float(response.json()['quality_score']) >= 0.50:
        return True
    return False
