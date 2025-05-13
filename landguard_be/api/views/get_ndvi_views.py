# import requests
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from ..serializers.ndvi_single import NDVICoordinatesSerializer
# from ..utils.auth_utils import get_sentinel_access_token
# from ..sentinel_hub_config import get_stats_request, get_headers

# class NDVIView(APIView):
#     def post(self, request):
#         # Validate input data using serializer
#         serializer = NDVICoordinatesSerializer(data=request.data)
#         print("request data is:", request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         coordinates = serializer.validated_data["coordinates"]
#         print("coordinates are: ", coordinates)

#         # Access token
#         token = get_sentinel_access_token()
#         if isinstance(token, Response):  # If it's an error response
#             return token
        
#         # Sentinel Hub Evalscript and API request
#         stats_request = get_stats_request(coordinates, already_wrapped=True)
#         print("Final Request Payload:", stats_request)
#         headers = get_headers(token)
#         url = "https://services.sentinel-hub.com/api/v1/statistics"

#         try:
#             response = requests.post(url, headers=headers, json=stats_request)
#             print("URL:", url)
#             print("Headers:", headers)
#             print("Request Payload:", stats_request)
#             print("Response Status Code:", response.status_code)
#             print("Response Content:", response.text)
#             response.raise_for_status()  # Raise HTTPError for bad status codes
#             data = response.json()
#         except requests.exceptions.RequestException as e:
#             return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
#         except ValueError:  # If response is not JSON
#             return Response({"error": "Invalid response from Sentinel Hub"}, status=status.HTTP_502_BAD_GATEWAY)

#         return Response({
#             "data":data
#         })



import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.ndvi_single import NDVICoordinatesSerializer
from ..utils.auth_utils import get_sentinel_access_token
from ..sentinel_hub_config import get_stats_request, get_headers
from ..utils.db_utils import get_mongo_collection

class getNDVIView(APIView):
    def post(self, request):
        # Validate input data using serializer
        serializer = NDVICoordinatesSerializer(data=request.data)
        print("request data is:", request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        coordinates = validated["coordinates"]
        from_date = validated["from_date"]
        to_date = validated["to_date"]
        interval_days = validated.get("interval_days")

        from_date_iso = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_date_iso = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        print("coordinates are: ", coordinates)

        # Get access token
        token = get_sentinel_access_token()
        if isinstance(token, Response):  # Error during token fetching
            return token

        # Build Sentinel Hub request
        stats_request = get_stats_request(
            coordinates,
            already_wrapped=True,
            from_date=from_date_iso,
            to_date=to_date_iso,
            interval_days=interval_days
        )

        headers = get_headers(token)
        url = "https://services.sentinel-hub.com/api/v1/statistics"

        try:
            response = requests.post(url, headers=headers, json=stats_request)
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.text)
            response.raise_for_status()
            data = response.json()

            interval_stats = []
            for entry in data["data"]:
                interval_info = entry.get("interval", {})
                stats_data = entry["outputs"]["ndvi"]["bands"]["B0"]["stats"]
                interval_stats.append({
                    "from": interval_info.get("from"),
                    "to": interval_info.get("to"),
                    "stats": stats_data
                })

        except (KeyError, IndexError):
            return Response({"error": "Unexpected response format from Sentinel Hub"}, status=status.HTTP_502_BAD_GATEWAY)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        # Save to MongoDB
        # collection = get_mongo_collection(collection_name="locations")
        # doc = {
        #     "coordinates": coordinates,
        #     "place_name": validated["place_name"],
        #     "area": validated["area"],
        #     "from_date": from_date.isoformat(),
        #     "to_date": to_date.isoformat(),
        #     "interval_days": interval_days,
        #     "ndvi_stats": interval_stats
        # }
        # print("📦 Inserting document into MongoDB:", doc)
        # insert_result = collection.insert_one(doc)
        # print("🆔 Inserted ID:", insert_result.inserted_id)

        # Return the response
        return Response({
            "coordinates": coordinates,
            "place_name": validated["place_name"],
            "area": validated["area"],
            "from_date": from_date_iso,
            "to_date": to_date_iso,
            "interval_days": interval_days,
            "ndvi_stats": interval_stats,
            "status": status.HTTP_200_OK
        })
