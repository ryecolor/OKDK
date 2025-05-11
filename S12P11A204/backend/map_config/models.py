from django.db import models

class MapConfig(models.Model):
    access_token = models.CharField(
        max_length=255,
        verbose_name="맵박스 액세스 토큰"
    )
    center_lat = models.FloatField(
        default=37.4979,
        verbose_name="기본 위도"
    )
    center_lng = models.FloatField(
        default=127.0286,
        verbose_name="기본 경도"
    )
    zoom = models.FloatField(
        default=16,
        verbose_name="초기 줌 레벨"
    )
    min_zoom = models.FloatField(
        default=10,
        verbose_name="최소 줌"
    )
    max_zoom = models.FloatField(
        default=18,
        verbose_name="최대 줌"
    )
    pitch = models.FloatField(
        default=45,
        verbose_name="3D 각도"
    )
    bearing = models.FloatField(
        default=-17.6,
        verbose_name="회전 각도"
    )
    flood_layer_url = models.URLField(
        max_length=600,  # URL 길이 제한 확장
        default='https://www.safemap.go.kr/openApiService/wms/getLayerData.do',
        verbose_name="침수 레이어 URL"
    )

    class Meta:
        verbose_name = "지도 설정"
        verbose_name_plural = "지도 설정"

class LegendItem(models.Model):
    color = models.CharField(
        max_length=7,
        verbose_name="색상 코드"
    )
    name = models.CharField(
        max_length=100,  # 길이 제한 확대
        verbose_name="등급 이름"
    )
    range = models.CharField(
        max_length=100,  # 길이 제한 확대
        verbose_name="범위 설명"
    )

    class Meta:
        verbose_name = "범례 항목"
        verbose_name_plural = "범례 항목"


# class DrainNode(models.Model):
#     location_x = models.DecimalField(max_digits=20, decimal_places=16)  # double precision에 맞춤
#     location_y = models.DecimalField(max_digits=20, decimal_places=16)  # double precision에 맞춤
#     state_img_url = models.CharField(max_length=200)
#     block = models.BigIntegerField()  # bigint 타입에 맞춤
    
#     class Meta:
#         db_table = 'Drain_drain'