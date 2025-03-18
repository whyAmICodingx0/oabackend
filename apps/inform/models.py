from django.db import models
from apps.oaauth.models import OAUser, OADepartment

class Inform(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # 如果前端上傳departments中包含了0，比如[0]，那麼就認為這個通知是所有部門可見
    public = models.BooleanField(default=False)
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='informs', related_query_name='informs')
    # departments: 序列化的時候用，前端上船部門id，我們通過department_ids來獲取
    departments = models.ManyToManyField(OADepartment, related_name='informs', related_query_name='informs')

    class Meta:
        ordering = ('-create_time',)

class InformRead(models.Model):
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    user = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    read_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # inform和user組合的數據，必須是唯一的
        unique_together = ('inform', 'user')