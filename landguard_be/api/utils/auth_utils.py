import requests
from rest_framework.response import Response
from rest_framework import status
from decouple import config

CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
TOKEN_URL = config("TOKEN_URL")

def get_sentinel_access_token():
    """
    Authenticates with Sentinel Hub and returns an access token.
    """
    token_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    token_response = requests.post(TOKEN_URL, data=token_data)
    if token_response.status_code != 200:
        return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

    access_token = token_response.json().get("access_token")
    if access_token:
        print("✅ got access token")
        return access_token
    if not access_token:
        return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)