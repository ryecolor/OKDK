# map_config/apps.py
from django.apps import AppConfig

# 🚨 클래스 이름과 name 필드 변경 필요
class MapConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map_config'  # ⬅️ 앱 이름을 'map_config'로 일치시켜야 함
