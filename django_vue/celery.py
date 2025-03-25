import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

# 設置django的settings模塊，celery會讀取這個模塊中的配置訊息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_vue.settings')

# 創建celery對象
app = Celery('django_vue')

## 日誌管理
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('celery.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# 配置從settins.py中讀取celery配置信息，所有Celery配置信息都要以CELERY_開頭
# broker_url => CELERY_BROKER_RUL
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動發現任務，任務可以寫在app/tasks.py中
app.autodiscover_tasks()

# 測試任務
# 1. bind=True，在任務函數中，第一個參數就是任務對象(Task)，如果沒有設置參數，或bind=False，那任務函數中就不會有任務對象參數
# 2. ignore_result=True，就不會保存任務執行的結果
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    # print(f'Request: {self.request!r}')
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')