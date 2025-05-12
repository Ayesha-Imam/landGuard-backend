from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.facebook_utils import post_to_facebook
from ..utils.generate_image_utils import generate_image_with_message

class FacebookPostView(APIView):
    def post(self, request):
        message = request.data.get("message", "Default message from LandGuard app")
        
        try:
            image_path = generate_image_with_message(message)
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Image generation failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        result = post_to_facebook(message, image_path)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)
