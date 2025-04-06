from django.db import models
from django.contrib.auth import get_user_model

OAUser = get_user_model()


class AbsentStatusChoices(models.IntegerChoices):
    # 審核中
    AUDITING = 1
    # 審核通過
    PASS = 2
    # 審核拒絕
    REJECT = 3


class AbsentType(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)


class Absent(models.Model):
    # 1. 標題
    title = models.CharField(max_length=200)
    # 2. 請假詳細內容
    request_content = models.TextField()
    # 3. 請假類型（事假、婚假）
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE, related_name='absents', related_query_name='absents')
    # 如果在一個模型中，有多個字段對同一個模型引用了外鍵，那麼必須指定 related_name 為不同的值
    # 4. 發起人
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='my_absents', related_query_name='my_absents')
    # 5. 審核人（可以為空）
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='sub_absents', related_query_name='sub_absents', null=True)
    # 6. 狀態
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.AUDITING)
    # 7. 請假開始日期
    start_date = models.DateField()
    # 8. 請假結束日期
    end_date = models.DateField()
    # 9. 請假發起時間
    create_time = models.DateTimeField(auto_now_add=True)
    # 10. 審核回覆內容
    response_content = models.TextField(blank=True)

    class Meta:
        ordering = ('-create_time', )