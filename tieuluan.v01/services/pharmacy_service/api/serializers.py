from rest_framework import serializers
from .models import Medication, Prescription

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    medication_names = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ('medications',)
        
    def get_medication_names(self, obj):
        return [med.name for med in obj.medications.all()]
