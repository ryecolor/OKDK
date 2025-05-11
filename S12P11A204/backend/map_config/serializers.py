from rest_framework import serializers
from .models import MapConfig, LegendItem

class LegendItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegendItem
        fields = ['color', 'name', 'range']

class MapConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapConfig
        exclude = ['id']
