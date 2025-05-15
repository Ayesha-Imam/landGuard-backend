import os
from urllib.parse import urlparse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from ..authentication import MongoJWTAuthentication
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
        username = request.data.get("username")
        contact = request.data.get("contact")
        description = request.data.get("description")
        image = request.FILES.get("image")

        if not title or not username or not contact or not location or not description:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        image_url = None
        if image:
            file_path = default_storage.save(f"land_images/{image.name}", image)
            image_url = request.build_absolute_uri(default_storage.url(file_path))

        land_collection = get_mongo_collection("posts")
        land_collection.insert_one({
            "title": title,
            "username": username,
            "contact": contact,
            "location": location,
            "description": description,
            "image_url": image_url,
            "user_id": ObjectId(str(request.user._id)),
            "created_at": datetime.now()
        })

        return Response({"detail": "Post created", "image_url": image_url}, status=status.HTTP_201_CREATED)


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

class DeleteLandPostView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, postId):
        user = request.user
        land_collection = get_mongo_collection("posts")

        # Validate postId format
        if not ObjectId.is_valid(postId):
            return Response({"detail": "Invalid post ID format"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the post and verify ownership
        post = land_collection.find_one({"_id": ObjectId(postId)})
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if str(post.get("user_id")) != str(user._id):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Handle image deletion
        if post.get("image_url"):
            try:
                # Extract the relative path from URL
                parsed_url = urlparse(post["image_url"])
                relative_path = parsed_url.path.split('/media/')[-1]
                
                # Construct proper storage path
                storage_path = os.path.join('land_images', os.path.basename(relative_path))
                
                # Verify the path is safe
                if not storage_path.startswith(('land_images/', 'land_images\\')):
                    raise ValueError("Invalid file path")
                
                # Delete using default_storage
                if default_storage.exists(storage_path):
                    default_storage.delete(storage_path)
            except Exception as e:
                print(f"Error deleting image: {str(e)}")
                # Continue with post deletion even if image deletion fails

        # Delete the post document
        land_collection.delete_one({"_id": ObjectId(postId)})

        return Response({"detail": "Post deleted successfully"}, status=status.HTTP_200_OK)