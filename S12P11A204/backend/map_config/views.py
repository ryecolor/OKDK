from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from drain.models import Drain
from .models import MapConfig, LegendItem
from .serializers import MapConfigSerializer, LegendItemSerializer

class MapConfigAPI(APIView):
    def get(self, request):
        config = MapConfig.objects.first()
        legends = LegendItem.objects.all()
        return Response({
            'config': MapConfigSerializer(config).data,
            'legends': LegendItemSerializer(legends, many=True).data
        })

def get_drain_data(request):
    try:
        drains = Drain.objects.all().values(
            'id', 'location_x', 'location_y', 'state_img_url'  # block 필드 제거
        )
        return JsonResponse(list(drains), safe=False)
    except Exception as e:
        print(f"Error in get_drain_data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
