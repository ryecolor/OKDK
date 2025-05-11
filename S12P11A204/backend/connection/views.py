from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.shortcuts import render

@api_view(['POST'])
def StartStreaming(request):
    return render(request, 'connection/streaming.html')
