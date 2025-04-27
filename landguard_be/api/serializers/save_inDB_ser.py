from rest_framework import serializers

class NDVICoordinatesSerializer(serializers.Serializer):
    area = serializers.CharField()
    place_name = serializers.CharField()
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.ListField(
                child=serializers.FloatField()
            ),
            min_length=3,  # At least 3 points for a valid polygon
        ),
        min_length=1,  # At least 1 polygon
    )
    # from_date = serializers.DateTimeField()  # Accepts ISO 8601 format
    # to_date = serializers.DateTimeField()
    # interval_days = serializers.IntegerField(required=False, default=30)
