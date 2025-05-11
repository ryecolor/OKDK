from django.db import models
from django.conf import settings
from region.models import District

# 로봇 정보를 저장하는 모델
class Robot(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    selected_drain = models.CharField(max_length=50, null=True, blank=True)
    is_robot_available = models.BooleanField()
    robot_unavailable_reason = models.TextField(default="", blank=True)
    
    def save(self, *args, **kwargs):
        if self.is_robot_available:
            self.robot_unavailable_reason = ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# 하드웨어에서 현재 로봇 상태를 전송받아 저장하는 모델
class RobotLog(models.Model):
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=20)
    log_content = models.TextField()
    def __str__(self):
        return self.robot.name

# 로봇의 수리 이력을 저장하는 모델
class RobotRepair(models.Model):
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    repair_date = models.DateTimeField(auto_now_add=True)
    repair_reason = models.TextField()
    repair_result = models.TextField()
    def __str__(self):
        return self.robot.name


# 하드웨어에서 보낸 로그를 저장하는 모델
class LogEntry(models.Model):
    robot_id = models.CharField(max_length=100)
    data = models.JSONField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.robot_id}"