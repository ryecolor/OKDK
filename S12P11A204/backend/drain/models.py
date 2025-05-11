from django.db import models
from region.models import Block

class Drain(models.Model):
    location_x = models.FloatField()
    location_y = models.FloatField()
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    state_img_url = models.URLField()
    def __str__(self):
        return f"Drain {self.id}"

class DrainRepair(models.Model):
    drain = models.ForeignKey(Drain, on_delete=models.CASCADE)
    repair_date = models.DateTimeField(auto_now_add=True)
    repair_result = models.TextField()
    def __str__(self):
        return f"DrainRepair {self.id}"
    
class DrainCondition(models.Model):
    drain = models.ForeignKey(Drain, on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=30, default='')
    def __str__(self):
        return f"DrainCondition {self.id}"    