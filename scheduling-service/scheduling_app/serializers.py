from rest_framework import serializers
from .models import AvailabilityTemplate, PitchSlot

class AvailabilityTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityTemplate
        fields = '__all__'

class PitchSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchSlot
        fields = '__all__'

class PitchSlotStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchSlot
        fields = ['status']
