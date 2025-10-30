from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Attendance

@receiver(post_save, sender=Attendance)
def recalculate_on_save(request, instance, **kwargs):
    # 給与計算が必要な場合のシグナル処理
    pass

@receiver(post_delete, sender=Attendance)
def recalculate_on_delete(request, instance, **kwargs):
    # 削除時の再計算処理
    pass