from core.models import CustomUser, Bike, BikeLocation, BikeRental
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class BikeLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)], required=True)
    longitude = serializers.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)], required=True)    

    class Meta:
        model = BikeLocation
        fields = [ 'bike','latitude', 'longitude', 'time']
        read_only_fields = ['bike','time',]

class BikeSerializer(serializers.ModelSerializer):
    keycode = serializers.CharField(max_length=8, default="0000", write_only=True)

    class Meta:
        model = Bike
        fields = ['url','id','status', 'keycode',] 
        read_only_fields = ['url','id', ]
    
    def validate_status(self, value):
        if self.instance:
            if BikeRental.objects.filter(bike=self.instance, end_time__isnull=True).exists() and value != 'B':
                raise serializers.ValidationError("Cannot update status while an active bikerental is ongoing")
        return value


class StartRentalSerializer(serializers.ModelSerializer):
    bike = serializers.PrimaryKeyRelatedField(queryset=Bike.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)

    class Meta:
        model = BikeRental
        fields = ['bike', 'user', 'start_time']
        read_only_fields = ['start_time']

    def create(self, validated_data):
        bike = validated_data['bike']
        bike.status = 'B'
        bike.save()
        return BikeRental.objects.create(**validated_data)

    def validate_bike(self, value):
        if not value.status == 'A':
            raise serializers.ValidationError("Bike is not available")
        return value

    def validate_user(self, value):
        try:
            if not value.subscription.is_valid():
                raise serializers.ValidationError("User has no valid subscription")
        except AttributeError:
            raise serializers.ValidationError("User has no valid subscription")
        if BikeRental.objects.filter(user=value, end_time__isnull=True).exists():
            raise serializers.ValidationError("User already have an ongoing bikerental")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['keycode'] = instance.bike.keycode
        return representation
    
class StopRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = ['bike', 'user', 'start_time', 'end_time']
        read_only_fields = fields