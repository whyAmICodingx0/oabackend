from django.core.management.base import BaseCommand
from apps.absent.models import AbsentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        absent_types = ["事假", "病假", "工傷假", "婚假", "喪假", "產假", "探親假", "公假", "年休假"]
        absents = []
        for absent_type in absent_types:
            absents.append(AbsentType(name=absent_type))
        AbsentType.objects.bulk_create(absents)
        self.stdout.write('請假類型數據初始化成功！')