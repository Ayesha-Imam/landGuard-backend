# from rest_framework import serializers

# class NDVIMultipleCoordinatesSerializer(serializers.Serializer):
#     coordinates_list = serializers.ListField(
#         child=serializers.ListField(
#             child=serializers.ListField(
#                 child=serializers.FloatField()
#             ),
#             min_length=5,  # Minimum 5 points to form a polygon
#         ),
#         min_length=1,  # At least one set of coordinates
#     )


from rest_framework import serializers

class LocationInputSerializer(serializers.Serializer):
    place_name = serializers.CharField()
    coordinates = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))
    interval_days = serializers.IntegerField()

class NDVIMultipleCoordinatesSerializer(serializers.Serializer):
    locations = LocationInputSerializer(many=True)
    from_date = serializers.DateTimeField(source="from")
    to_date = serializers.DateTimeField(source="to")
