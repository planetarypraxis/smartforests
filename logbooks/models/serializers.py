from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User


class UserField(serializers.Field):
    def to_representation(self, value):
        return UserSerializer(value)

    def to_internal_value(self, data):
        return None


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'id', ]


class PageCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = 'logbooks.GeocodedMixin'
        geo_field = "coordinates"
        fields = '__all__'
