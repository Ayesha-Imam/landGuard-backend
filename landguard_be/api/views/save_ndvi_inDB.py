import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers.save_inDB_ser import NDVICoordinatesSerializer
from ..utils.auth_utils import get_sentinel_access_token
from ..sentinel_hub_config import get_stats_request, get_headers
from ..utils.db_utils import get_mongo_collection  
from datetime import datetime, timedelta

class saveNDVIView(APIView):
    def post(self, request):
        serializer = NDVICoordinatesSerializer(data=request.data)
        print("request data is:", request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        coordinates = validated["coordinates"]

        # Automatically set from_date, to_date, and interval
        from datetime import datetime, timedelta
        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=30)
        interval_days = 30

        # Convert to ISO format
        from_date_iso = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_date_iso = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        print("coordinates are: ", coordinates)
        print(f"Fetching NDVI from {from_date_iso} to {to_date_iso} with {interval_days} days interval.")

        # Access token
        token = get_sentinel_access_token()
        if isinstance(token, Response):
            return token
        
        stats_request = get_stats_request(
            coordinates,
            already_wrapped=True,
            from_date=from_date_iso,
            to_date=to_date_iso,
            interval_days=interval_days
        )
        print("Final Request Payload:", stats_request)
        headers = get_headers(token)
        url = "https://services.sentinel-hub.com/api/v1/statistics"

        try:
            response = requests.post(url, headers=headers, json=stats_request)
            print("URL:", url)
            print("Headers:", headers)
            print("Request Payload:", stats_request)
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.text)
            response.raise_for_status()
            data = response.json()
            stats = data["data"][0]["outputs"]["ndvi"]["bands"]["B0"]["stats"]
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e), "details": response.text}, status=response.status_code)
        except (KeyError, IndexError) as e:
            return Response({"error": "Unexpected response format", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        # Save to MongoDB
        collection = get_mongo_collection(collection_name="locations")
        doc = {
            "coordinates": coordinates,
            "place_name": validated["place_name"],
            "area": validated["area"],
            "from_date": from_date_iso,
            "to_date": to_date_iso,
            "interval_days": interval_days,
            "ndvi_stats": stats
        }
        print("📦 Inserting document into MongoDB:", doc)
        insert_result = collection.insert_one(doc)
        print("🆔 Inserted ID:", insert_result.inserted_id)

        # Add the inserted_id (converted to string) to the doc
        doc["_id"] = str(insert_result.inserted_id)

        return Response(doc, status=status.HTTP_201_CREATED)
