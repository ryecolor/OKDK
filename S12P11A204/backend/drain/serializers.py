from rest_framework import serializers
from .models import Drain, DrainCondition

class DrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drain
        fields = '__all__'

class RecieveImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drain
        fields = ['id', 'state_img_url', 'check_date', 'drain_condition']


class DrainConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrainCondition
        fields = '__all__'               