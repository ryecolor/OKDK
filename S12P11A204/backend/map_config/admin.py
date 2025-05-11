# map_config/admin.py
from django.contrib import admin
from .models import MapConfig, LegendItem  # ⬅️ 앱 내부 임포트 확인

admin.site.register(MapConfig)
admin.site.register(LegendItem)
