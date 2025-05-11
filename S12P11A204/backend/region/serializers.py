from rest_framework import serializers
from .models import  Block, BlockCondition



class BlockConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockCondition
        fields = '__all__'               

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['selected_robot']        