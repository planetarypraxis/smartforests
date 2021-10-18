from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'id', ]


class StoryCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = 'logbooks.StoryPage'
        geo_field = "coordinates"
        fields = '__all__'


class LogbookCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = 'logbooks.LogbookPage'
        geo_field = "coordinates"
        fields = '__all__'
