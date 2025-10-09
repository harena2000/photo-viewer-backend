from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

latest_layers = []

@api_view(['POST'])
def update_layers(request):
    global latest_layers
    latest_layers = request.data.get("layers", [])
    print(latest_layers)
    return Response({"status": "ok"})

@api_view(['GET'])
def get_layers(request):
    return Response({"layers": latest_layers})
