from asyncio import exceptions
from bson import ObjectId
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from .utils.db_utils import get_mongo_collection
from .utils.auth_token_utils import is_token_blacklisted

class MongoUser:
    def __init__(self, user_data):
        self.user_data = user_data
        self._id = user_data["_id"]
        self.email = user_data["email"]
        self.username = user_data["username"]
        self.is_authenticated = True

    def __getitem__(self, key):
        return self.user_data[key]

class MongoJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        # ❗ Check if token has been blacklisted
        jti = validated_token.get("jti")
        if jti and is_token_blacklisted(jti):
            raise AuthenticationFailed("Token has been blacklisted.")

        # Assuming you are decoding user ID from the token:
        user_id = validated_token.get("user_id")  # or "_id" if you store it that way
        if user_id is None:
            raise exceptions.AuthenticationFailed("Invalid token")

        # Now fetch the user from MongoDB
        user_collection = get_mongo_collection(collection_name="users")
        user_data = user_collection.find_one({"_id": ObjectId(user_id)})
        if user_data is None:
            raise exceptions.AuthenticationFailed("User not found")

        # ✅ Now user_data is defined, so this works:
        return (MongoUser(user_data), validated_token)

