"""
Views for the Pedal Power API
Provides endpoints for downsampled data and session detection
"""
from django.db.models import Avg
from django.db.models.functions import TruncSecond
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Telemetry
from .serializers import (
    TelemetrySerializer, 
    DownsampledDataSerializer,
    SessionSerializer
)


class DashboardView(TemplateView):
    """Dashboard view for visualizing telemetry data"""
    template_name = 'pedalpower/dashboard.html'


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for telemetry data
    Provides raw data and downsampled/session detection endpoints
    """
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
    
    def get_queryset(self):
        queryset = Telemetry.objects.all()
        
        # Filter by device_id if provided
        device_id = self.request.query_params.get('device_id', None)
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        # Filter by time range
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)
        
        if start_time:
            queryset = queryset.filter(server_timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(server_timestamp__lte=end_time)
            
        return queryset.order_by('server_timestamp')
    
    @action(detail=False, methods=['get'])
    def downsampled(self, request):
        """
        Get downsampled data at 1 Hz
        Averages all samples within each 1-second window
        """
        queryset = self.get_queryset()
        
        # Group by second and calculate averages
        downsampled = queryset.annotate(
            second=TruncSecond('server_timestamp')
        ).values('second').annotate(
            avg_voltage=Avg('voltage'),
            avg_current=Avg('current'),
            avg_power=Avg('power'),
        ).order_by('second')
        
        # Calculate cumulative energy (Wh)
        result = []
        cumulative_wh = 0.0
        
        for item in downsampled:
            # Energy = Power * Time (in hours)
            # 1 second = 1/3600 hours
            energy_increment = item['avg_power'] / 3600.0
            cumulative_wh += energy_increment
            
            result.append({
                'timestamp': item['second'],
                'avg_voltage': item['avg_voltage'],
                'avg_current': item['avg_current'],
                'avg_power': item['avg_power'],
                'energy_wh': cumulative_wh,
            })
        
        serializer = DownsampledDataSerializer(result, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """
        Detect sessions based on power thresholds
        A session starts when power > threshold and ends when power < threshold
        """
        # Get parameters
        power_threshold = float(request.query_params.get('threshold', '10.0'))
        gap_seconds = int(request.query_params.get('gap_seconds', '30'))
        
        queryset = self.get_queryset()
        
        # Get downsampled data first (1 Hz)
        downsampled = list(queryset.annotate(
            second=TruncSecond('server_timestamp')
        ).values('second', 'device_id').annotate(
            avg_power=Avg('power'),
            avg_voltage=Avg('voltage'),
            avg_current=Avg('current'),
        ).order_by('second'))
        
        if not downsampled:
            return Response([])
        
        # Detect sessions
        sessions = []
        current_session = None
        session_id = 0
        
        for i, item in enumerate(downsampled):
            power = item['avg_power']
            timestamp = item['second']
            device_id = item['device_id']
            
            if power >= power_threshold:
                if current_session is None:
                    # Start new session
                    session_id += 1
                    current_session = {
                        'session_id': session_id,
                        'device_id': device_id,
                        'start_time': timestamp,
                        'data_points': [item],
                    }
                else:
                    # Continue session
                    current_session['data_points'].append(item)
            else:
                if current_session is not None:
                    # Check if gap is too large
                    if i > 0:
                        time_gap = (timestamp - current_session['data_points'][-1]['second']).total_seconds()
                        if time_gap > gap_seconds:
                            # End current session
                            sessions.append(self._finalize_session(current_session))
                            current_session = None
        
        # Finalize last session if exists
        if current_session is not None:
            sessions.append(self._finalize_session(current_session))
        
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    def _finalize_session(self, session):
        """Calculate session statistics"""
        data_points = session['data_points']
        
        start_time = data_points[0]['second']
        end_time = data_points[-1]['second']
        duration = (end_time - start_time).total_seconds()
        
        # Calculate total energy (Wh)
        total_energy_wh = sum(dp['avg_power'] / 3600.0 for dp in data_points)
        
        # Calculate statistics
        powers = [dp['avg_power'] for dp in data_points]
        avg_power = sum(powers) / len(powers) if powers else 0
        max_power = max(powers) if powers else 0
        
        return {
            'session_id': session['session_id'],
            'device_id': session['device_id'],
            'start_time': start_time,
            'end_time': end_time,
            'duration_seconds': duration,
            'total_energy_wh': total_energy_wh,
            'avg_power': avg_power,
            'max_power': max_power,
        }
