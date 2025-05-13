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
        places = request.data.get("locations", [])
        if not places:
            return Response({"error": "No locations provided."}, status=status.HTTP_400_BAD_REQUEST)

        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=30)
        interval_days = 30

        from_date_iso = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_date_iso = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        token = get_sentinel_access_token()
        if isinstance(token, Response):
            return token

        headers = get_headers(token)
        url = "https://services.sentinel-hub.com/api/v1/statistics"
        collection = get_mongo_collection(collection_name="locations")

        results = []

        for place in places:
            serializer = NDVICoordinatesSerializer(data=place)
            if not serializer.is_valid():
                results.append({"place_name": place.get("place_name"), "error": serializer.errors})
                continue

            validated = serializer.validated_data
            coordinates = validated["coordinates"]
            place_name = validated["place_name"]
            area = validated["area"]

            # Check for duplicates
            if collection.find_one({"place_name": place_name, "coordinates": coordinates}):
                results.append({"place_name": place_name, "error": "Duplicate entry"})
                continue

            # Prepare stats request for this place
            stats_request = get_stats_request(
                coordinates,
                already_wrapped=True,
                from_date=from_date_iso,
                to_date=to_date_iso,
                interval_days=interval_days
            )

            try:
                response = requests.post(url, headers=headers, json=stats_request)
                response.raise_for_status()
                data = response.json()
                stats = data["data"][0]["outputs"]["ndvi"]["bands"]["B0"]["stats"]
            except (requests.exceptions.RequestException, KeyError, IndexError) as e:
                results.append({"place_name": place_name, "error": f"Failed to fetch stats: {str(e)}"})
                continue

            # Save to DB
            doc = {
                "coordinates": coordinates,
                "place_name": place_name,
                "area": area,
                "from_date": from_date_iso,
                "to_date": to_date_iso,
                "interval_days": interval_days,
                "ndvi_stats": stats
            }

            insert_result = collection.insert_one(doc)
            doc["_id"] = str(insert_result.inserted_id)
            results.append({"status": "Inserted", "doc": doc})

        successes = [r for r in results if r.get("status") == "Inserted"]
        failures = [r for r in results if "error" in r]

        if len(successes) == len(results):
            return Response(results, status=status.HTTP_201_CREATED)
        elif successes:
            return Response(results, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response(results, status=status.HTTP_400_BAD_REQUEST)


