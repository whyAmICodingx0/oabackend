from django.core.management.base import BaseCommand
from apps.oaauth.models import OADepartment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化部門數據
        boarder = OADepartment.objects.create(name='董事會', intro="董事會")
        developer = OADepartment.objects.create(name='產品開發部', intro="產品設計，技術開發")
        operator = OADepartment.objects.create(name='運營部', intro="客戶營運，產品營運")
        saler = OADepartment.objects.create(name='銷售部', intro="銷售產品")
        hr = OADepartment.objects.create(name='人事部', intro="員工招聘，員工培訓，員工考核")
        finance = OADepartment.objects.create(name='財務部', intro="財務報表，財務審核")
        self.stdout.write('部門數據初始化成功')