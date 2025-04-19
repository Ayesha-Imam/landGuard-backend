import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.ndvi_multiple import NDVIMultipleCoordinatesSerializer
from ..utils.auth_utils import get_sentinel_access_token
from ..sentinel_hub_config import get_stats_request, get_headers

# class NDVIMultiView(APIView):
#     def post(self, request):
#         # Validate input data using serializer
#         serializer = NDVIMultipleCoordinatesSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         coordinates_list = serializer.validated_data["coordinates_list"]
#         token = get_sentinel_access_token()
#         if isinstance(token, Response):  # If it's an error response
#             return token

#         headers = get_headers(token)
#         url = "https://services.sentinel-hub.com/api/v1/statistics"

#         results = []
        
        

#         try:
#             for coordinates in coordinates_list:
#                 stats_request = get_stats_request(coordinates, already_wrapped=False)
#                 print(f"Sending request for coordinates: {coordinates}")
#                 print("Request payload:", json.dumps(stats_request, indent=2))
#                 response = requests.post(url, headers=headers, json=stats_request)
#                 print("Status Code:", response.status_code)
#                 print("Response Body:", response.text)
#                 response.raise_for_status() 
#                 data = response.json()
#                 results.append({"coordinates": coordinates, "ndvi_data": data})
                
#         except requests.exceptions.RequestException as e:
#             results.append({"coordinates": coordinates, "error": str(e)})
#         except ValueError:  # If response is not JSON
#             results.append({"coordinates": coordinates, "error": "Invalid response from Sentinel Hub"})

#         return Response({"results": results})

from ..utils.db_utils import get_mongo_collection

class NDVIMultiView(APIView):
    def post(self, request):
        serializer = NDVIMultipleCoordinatesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        locations = validated_data["locations"]
        from_date = validated_data["from"]
        to_date = validated_data["to"]

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
            interval_days = loc["interval_days"]

            stats_request = get_stats_request(
                coordinates,
                already_wrapped=False,
                from_date=from_date,
                to_date=to_date,
                interval_days=interval_days
            )

            try:
                response = requests.post(url, headers=headers, json=stats_request)
                response.raise_for_status()
                data = response.json()

                # Save to DB
                collection.insert_one({
                    "place_name": place_name,
                    "coordinates": coordinates,
                    "interval_days": interval_days,
                    "from": from_date,
                    "to": to_date,
                    "ndvi_data": data
                })

                results.append({
                    "place_name": place_name,
                    "coordinates": coordinates,
                    "ndvi_data": data
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

        return Response({"results": results})
