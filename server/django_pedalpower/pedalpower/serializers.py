"""
Serializers for the Pedal Power API
"""
from rest_framework import serializers
from .models import Telemetry


class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ['id', 'server_timestamp', 'device_id', 'sequence_number', 
                  'voltage', 'current', 'power', 'created_at']


class DownsampledDataSerializer(serializers.Serializer):
    """Serializer for downsampled telemetry data"""
    timestamp = serializers.DateTimeField()
    avg_voltage = serializers.FloatField()
    avg_current = serializers.FloatField()
    avg_power = serializers.FloatField()
    energy_wh = serializers.FloatField()


class SessionSerializer(serializers.Serializer):
    """Serializer for detected sessions"""
    session_id = serializers.IntegerField()
    device_id = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    duration_seconds = serializers.FloatField()
    total_energy_wh = serializers.FloatField()
    avg_power = serializers.FloatField()
    max_power = serializers.FloatField()
