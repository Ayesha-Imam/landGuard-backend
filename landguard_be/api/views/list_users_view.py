from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.db_utils import get_mongo_collection

class ListAllUsersViews(APIView):
    def get(self, request):
        # Get the 'locations' collection
        collection = get_mongo_collection(collection_name="users")

        # Fetch all documents
        documents = list(collection.find({}, {"_id": 0, "password": 0})) 

        return Response(documents, status=status.HTTP_200_OK)
