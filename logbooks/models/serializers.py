from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from smartforests.models import User


class UserField(serializers.Field):
    def to_representation(self, value):
        return UserSerializer(value)

    def to_internal_value(self, data):
        if isinstance(data, User):
            return data
        elif isinstance(data, int):
            return User.objects.get(pk=data)
        elif isinstance(data, str):
            return User.objects.get(username=data)
        else:
            raise serializers.ValidationError("Invalid user")


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }


class PageCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = 'logbooks.GeocodedMixin'
        geo_field = "coordinates"
        fields = '__all__'
