# # views/social.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from ..utils.facebook_utils import post_to_facebook  # adjust path if needed

# class FacebookPostView(APIView):
#     def post(self, request):
#         message = request.data.get("message", "Default message from LandGuard app")
#         result = post_to_facebook(message)
        
#         if "error" in result:
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         return Response(result, status=status.HTTP_200_OK)


# views/social.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from django.conf import settings
from ..utils.facebook_utils import post_to_facebook  # Adjust path if needed

class FacebookPostView(APIView):
    def post(self, request):
        # Get message and image name from the request data
        message = request.data.get("message", "Default message from LandGuard app")
        image_name = request.data.get("image_name")  # Get the image name
        
        if not image_name:
            return Response({"error": "Image name is required!"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Build the full image path
        image_path = os.path.join(settings.BASE_DIR, "templates", image_name)  # Adjust path if necessary
        
        if not os.path.exists(image_path):
            return Response({"error": "Image not found!"}, status=status.HTTP_404_NOT_FOUND)
        
        # Call the function to post the image to Facebook
        result = post_to_facebook(message, image_path)
        
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)
