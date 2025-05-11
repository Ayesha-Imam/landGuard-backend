# views/social.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.facebook_utils import post_to_facebook  # adjust path if needed

class FacebookPostView(APIView):
    def post(self, request):
        message = request.data.get("message", "Default message from LandGuard app")
        result = post_to_facebook(message)
        
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
