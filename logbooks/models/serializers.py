from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'id', ]


class PageCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = 'logbooks.GeocodedMixin'
        geo_field = "coordinates"
        fields = '__all__'


class RichTextSerializer(serializers.Serializer):
    html = serializers.CharField(max_length=10000000)
