from django.db import models

class District(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Block(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='blocks') # 관리구역 참조
    # location_x = models.FloatField()
    # location_y = models.FloatField()
    selected_robot = models.CharField(max_length=50, null=True) # 선택된 로봇
    Cumulative_state_score = models.FloatField() # 누적 상태 점수
    Flooding_sensitivity = models.FloatField() # 현재 침수 민감도 계산방식에 따라서 타입 수정이 필요할 수 있음
    Flood_Image = models.ImageField(null=True) # 침수 이미지
    def __str__(self):
        return self.name
    

class BlockCondition(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now=True)
    condition = models.FloatField()
    def __str__(self):
        return self.block.name