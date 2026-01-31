"""
Models for Pedal Power telemetry data.
Uses an existing telemetry table created by the MQTT ingestor.
"""
from django.db import models


class Telemetry(models.Model):
    """
    Raw telemetry data from bikes
    This is a Django model for an existing database table
    """
    id = models.AutoField(primary_key=True)
    server_timestamp = models.DateTimeField(db_index=True)
    device_id = models.CharField(max_length=50, db_index=True)
    sequence_number = models.IntegerField()
    voltage = models.FloatField()
    current = models.FloatField()
    power = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'telemetry'
        managed = False  # Don't let Django manage this table
        ordering = ['-server_timestamp']
        indexes = [
            models.Index(fields=['device_id', 'server_timestamp']),
            models.Index(fields=['server_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device_id} @ {self.server_timestamp}: {self.power}W"
