from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.auth_token_utils import blacklist_token, is_token_blacklisted
import jwt

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        access_token = request.data.get("access") 

        if not refresh_token or not access_token:
            return Response({"detail": "Both refresh and access tokens required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access = AccessToken(access_token)

            if is_token_blacklisted(refresh['jti']) and is_token_blacklisted(access['jti']):
                return Response({"detail": "Already logged out."}, status=status.HTTP_200_OK)

            # Blacklist both tokens
            blacklist_token(refresh['jti'])
            blacklist_token(access['jti'])

            return Response({"detail": "Logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             refresh_token = request.data.get("refresh")
#             token = RefreshToken(refresh_token)
#             token.blacklist()

#             return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
#         except TokenError as e:
#             return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)