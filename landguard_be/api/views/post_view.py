from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.files.storage import default_storage
from bson import ObjectId
from datetime import datetime
from ..utils.db_utils import get_mongo_collection


class CreateLandPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        title = request.data.get("title")
        location = request.data.get("location")
        description = request.data.get("description")
        image = request.FILES.get("image")

        if not title or not location or not description:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        image_url = None
        if image:
            file_path = default_storage.save(f"land_images/{image.name}", image)
            image_url = default_storage.url(file_path)

        land_collection = get_mongo_collection("posts")
        land_collection.insert_one({
            "title": title,
            "location": location,
            "description": description,
            "image_url": image_url,
            "user_id": ObjectId(str(request.user._id)),
            "created_at": datetime.now()
        })

        return Response({"detail": "Post created"}, status=status.HTTP_201_CREATED)


class AllLandPostsView(APIView):
    def get(self, request):
        land_collection = get_mongo_collection("posts")
        posts = list(land_collection.find().sort("created_at", -1))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["user_id"] = str(post["user_id"])

        return Response(posts, status=status.HTTP_200_OK)


class MyLandPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        land_collection = get_mongo_collection("posts")
        posts = list(land_collection.find({"user_id": ObjectId(str(request.user._id))}).sort("created_at", -1))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["user_id"] = str(post["user_id"])

        return Response(posts, status=status.HTTP_200_OK)
