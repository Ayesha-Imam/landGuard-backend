import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.ndvi_multiple import NDVIMultipleCoordinatesSerializer
from ..utils.auth_utils import get_sentinel_access_token
from ..sentinel_hub_config import get_stats_request, get_headers

from ..utils.db_utils import get_mongo_collection

from datetime import datetime, timedelta

class NDVIMultiView(APIView):
    def post(self, request):
        serializer = NDVIMultipleCoordinatesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        locations = validated_data.get("locations", [])

        # Set dates
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        interval_days = 30

        # Format to ISO with timezone
        from_date_iso = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_date_iso = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Fetching NDVI from {from_date_iso} to {to_date_iso} with {interval_days} days interval.")

        token = get_sentinel_access_token()
        if isinstance(token, Response):
            return token

        headers = get_headers(token)
        url = "https://services.sentinel-hub.com/api/v1/statistics"
        collection = get_mongo_collection(collection_name="locations")
        results = []

        for loc in locations:
            place_name = loc["place_name"]
            coordinates = loc["coordinates"]

            # Search the document with matching coordinates
            existing_doc = collection.find_one({"coordinates": coordinates})

            if not existing_doc:
                results.append({
                    "place_name": place_name,
                    "coordinates": coordinates,
                    "error": "Location not found in database"
                })
                continue

            # Prepare stats request
            stats_request = get_stats_request(
                coordinates,
                already_wrapped=False,
                from_date=from_date_iso,
                to_date=to_date_iso,
                interval_days=interval_days
            )

            try:
                response = requests.post(url, headers=headers, json=stats_request)
                print("Response Status Code:", response.status_code)
                print("Response Content:", response.text)
                response.raise_for_status()
                data = response.json()

                # Extract only stats part
                stats_data = data["data"][0]["outputs"]["ndvi"]["bands"]["B0"]["stats"]

                # Update the document
                update_fields = {
                    "from_date": from_date_iso,
                    "to_date": to_date_iso,
                    "interval_days": interval_days,
                    "ndvi_stats": stats_data
                }

                collection.update_one(
                    {"_id": existing_doc["_id"]},
                    {"$set": update_fields}
                )

                results.append({
                    "place_name": place_name,
                    "message": "Updated successfully"
                })

            except requests.exceptions.RequestException as e:
                results.append({
                    "place_name": place_name,
                    "coordinates": coordinates,
                    "error": str(e)
                })
            except ValueError:
                results.append({
                    "place_name": place_name,
                    "coordinates": coordinates,
                    "error": "Invalid JSON response"
                })

        return Response({"results": results}, status=status.HTTP_200_OK)
