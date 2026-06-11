from rest_framework import serializers
from .models import Encounter, LabTest

class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'

class EncounterSerializer(serializers.ModelSerializer):
    lab_tests = LabTestSerializer(many=True, read_only=True)

    class Meta:
        model = Encounter
        fields = '__all__'
