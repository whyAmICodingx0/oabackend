from django.core.management import BaseCommand
from apps.oaauth.models import OAUser, OADepartment


class Command(BaseCommand):
    def handle(self, *args, **options):
        boarder = OADepartment.objects.get(name='董事會')
        developer = OADepartment.objects.get(name='產品開發部')
        operator = OADepartment.objects.get(name='運營部')
        saler = OADepartment.objects.get(name='銷售部')
        hr = OADepartment.objects.get(name='人事部')
        finance = OADepartment.objects.get(name='財務部')

        # 1. 東東: 屬於董事會的leader
        dongdong = OAUser.objects.create_superuser(email='dongdong@gmail.com', realname='東東', password='111111',
                                                   department=boarder)
        # 2. 多多: 董事會
        duoduo = OAUser.objects.create_superuser(email="duoduo@gmail.com", realname='多多', password='111111',
                                                 department=boarder)
        # 3. 張三，產品開發部的 leader
        zhangsan = OAUser.objects.create_user(email="zhangsan@gmail.com", realname='張三', password='111111',
                                              department=developer)
        # 4. 李四，運營部 leader
        lisi = OAUser.objects.create_user(email="lisi@gmail.com", realname='李四', password='111111',
                                          department=operator)
        # 5. 王五，人事部的 leader
        wangwu = OAUser.objects.create_user(email="wangwu@gmail.com", realname='王五', password='111111',
                                            department=hr)
        # 6. 趙六，財務部的 leader
        zhaoliu = OAUser.objects.create_user(email="zhaoliu@gmail.com", realname='趙六', password='111111',
                                             department=finance)
        # 7. 孫七，銷售部的 leader
        sunqi = OAUser.objects.create_user(email="sunqi@gmail.com", realname='孫七', password='111111',
                                           department=saler)

        # 給部門指定leader和manager
        # 公司：人工智能公司、运营部、销售部
        # 多人：人事部、财务部

        # 1. 董事会
        boarder.leader = dongdong
        boarder.manager = None

        # 2. 產品開發部
        developer.leader = zhangsan
        developer.manager = dongdong

        # 3. 運營部
        operator.leader = lisi
        operator.manager = dongdong

        # 4. 銷售部
        saler.leader = sunqi
        saler.manager = dongdong

        # 5. 人事資源
        hr.leader = wangwu
        hr.manager = duoduo

        # 6. 財務部
        finance.leader = zhaoliu
        finance.manager = duoduo

        boarder.save()
        developer.save()
        operator.save()
        saler.save()
        hr.save()
        finance.save()

        self.stdout.write('初始用戶創建成功')