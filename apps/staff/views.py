from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment, UserStatusChoices
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer, ActiveStaffSerializer, StaffUploadSerializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from utils import aeser
from django.urls import reverse
from django_vue.celery import debug_task
from .task import send_mail_task
from django.http.response import JsonResponse
from urllib import parse
from rest_framework import generics
from rest_framework import exceptions
from apps.oaauth.serializers import UserSerializer
from .paginations import StaffListPagination
from rest_framework import viewsets
from rest_framework import mixins
from datetime import datetime
import json
import pandas as pd
from django.http.response import HttpResponse
from django.db import transaction

OAUser = get_user_model()

aes = aeser.AESCipher(settings.SECRET_KEY)


def send_active_email(request, email):
    token = aes.encrypt(email)
    # /staff/active?token=xxx
    active_path = reverse('staff:active_staff') + '?' + parse.urlencode({'token': token})
    # http://127.0.0.1:8000/staff/active?token=xxx
    active_url = request.build_absolute_uri(active_path)
    # 發送一個連結，讓用戶點集連結後，跳轉到啟用頁面，才能啟用
    # 為了區分用戶，在發送連結中，該連結中應該要包含這個用戶的信箱
    # 針對信箱要進行加密:AES
    message = f'請點集以下連結啟用帳號: {active_url}'
    subject = f'帳號啟用通知'
    # send_mail(f'帳號啟用通知', recipient_list=[email], message=message, from_email=settings.DEFAULT_FROM_EMAIL)
    send_mail_task.delay(email, subject, message)


class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all().order_by('id')
    serializer_class = DepartmentSerializer

# 啟用員工的過程
# 1. 用戶訪問啟用連結的時候，會返回含有表單的頁面，是圖中可以獲取到token，為了在用戶提交表單的時候
# post函數中能知道這個token，我們可以在返回頁面之前，先把token儲存在cookie中
# 2. 較驗用戶上傳的信箱和密碼是否正確，並且解密token中的信箱，與用戶提交的信箱進行對比，如果都相同那麼就是啟用成功
class ActiveStaffView(APIView):
    def get(self, request):
        # http://127.0.0.1:8000/staff/active?token=BCD2PO8XseQlm%2F1vA5ZxMAbKzIIiNoczdgvcV6Mod88MaX3brZbM9ICg0F0iEN5B
        token = request.GET.get('token')
        response = render(request, 'active.html')
        response.set_cookie('token', token)
        return response

    def post(self, request):
        try:
            token = request.COOKIES.get('token')
            email = aes.decrypt(token)
            serializer = ActiveStaffSerializer(data=request.POST)
            if serializer.is_valid():
                print(serializer.data)
                form_email = serializer.validated_data.get('email')
                user = serializer.validated_data.get('user')
                print(user)
                if email != form_email:
                    return JsonResponse({'code': 400, 'message': '信箱錯誤'})
                user.status = UserStatusChoices.ACTIVED
                user.save()
                return JsonResponse({'code': 200, 'message': ''})
            else:
                detail = list(serializer.errors.values())[0][0]
                return JsonResponse({'code': 400, 'message': detail})
        except Exception as e:
            return JsonResponse({'code': 400, 'message': 'token錯誤'})

class StaffViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin
):
    queryset = OAUser.objects.all()
    pagination_class = StaffListPagination

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT']:
            return UserSerializer
        else:
            return AddStaffSerializer

    # 員工列表
    def get_queryset(self):
        department_id = self.request.query_params.get('department_id')
        realname = self.request.query_params.get('realname')
        date_joined = self.request.query_params.getlist('date_joined[]')

        queryset = self.queryset
        # 返回員工列表邏輯:
        # 1. 如果是董事會的，那麼返回所有員工
        # 2. 如果不是董事會的，但是是部門leader，那麼就返回部門員工
        # 3. 如果不是董事會也不是部門leader，就拋出403 Forbidden錯誤
        user = self.request.user
        if user.department.name != '董事會':
            if user.uid != user.department.leader.uid:
                raise exceptions.PermissionDenied
            else:
                queryset = queryset.filter(department_id=user.department_id)
        else:
            if department_id:
                queryset = queryset.filter(department_id=department_id)

        if realname:
            queryset = queryset.filter(realname__icontains=realname)
        if date_joined:
            # ['2024-10-01', '2024-10-10']
            try:
                start_date = datetime.strptime(date_joined[0], '%Y-%m-%d')
                end_date = datetime.strptime(date_joined[1], '%Y-%m-%d')
                queryset = queryset.filter(date_joined__range=(start_date, end_date))
            except Exception:
                print('日期出錯但不處理')

        return queryset.order_by("-date_joined").all()

    # 增新員工
    def create(self, request, *args, **kwargs):
        # 如果用的是視圖集，那麼視圖集會自動把request放到context中
        # 如果是直接繼承自APIView，那麼就需要手動將request對象傳給serializers.context中
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data['realname']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 1. 保存用戶數具
            department = request.user.department
            user = OAUser.objects.create_user(email=email, realname=realname, password=password, department=department)
            # user.department = department
            # user.save()

            # 2. 發送啟用信箱 I/O: 網路請求、文件讀寫
            send_active_email(request, email)

            return Response()
        else:
            return Response(data={'detail': list(serializer.errors.value())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # 可以單獨修改設置
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)



class StaffDownloadView(APIView):
    def get(self, request):
        # /staff/download?pks=[x,y]
        # ['x', 'y',] -> json格式的字符串
        pks = request.query_params.get('pks')
        try:
            pks = json.loads(pks)
        except Exception:
            return Response({'datail': '員工參數錯誤'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            current_user = request.user
            queryset = OAUser.objects
            if current_user.department.name != '董事會':
                if current_user.department.leader_id != current_user.uid:
                    return Response({'detail': '沒有權限下載'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    # 如果是部門的leader，那麼就先過濾為部門的員工
                    queryset = queryset.filter(department_id=current_user.department_id)
            queryset = queryset.filter(pk__in=pks)
            result = queryset.values("realname", "email", "department__name", "date_joined", "status")
            staff_df = pd.DataFrame(list(result))
            staff_df = staff_df.rename(
                columns={'realname': '姓名', 'email': '信箱', 'department__name': '部門', 'date_joined': '入職時間',
                         'status': '狀態'})
            response = HttpResponse(content_type='application/xlsx')
            response['Content-Disposition'] = 'attachment; filename="員工訊息.xlsx"'
            # 把staff_df寫入到Response中
            with pd.ExcelWriter(response) as writer:
                staff_df.to_excel(writer, sheet_name='員工訊息')
            return response
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StaffUploadView(APIView):
    def post(self, request):
        serializer = StaffUploadSerializers(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')
            current_user = request.user
            if current_user.department.name != '董事會' or current_user.department.leader_id != current_user.uid:
                return Response({'detail': '你沒有權限訪問'}, status=status.HTTP_403_FORBIDDEN)

            staff_df = pd.read_excel(file)
            users = []
            for index, row in staff_df.iterrows():
                # 獲取部門
                if current_user.department.name != '董事會':
                    department = current_user.department
                else:
                    try:
                        department = OADepartment.objects.filter(name=row['部門']).first()
                        if not department:
                            return Response(f'{row['部門']}不存在', status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response(f'部門列不存在', status=status.HTTP_400_BAD_REQUEST)
                try:
                    email = row['信箱']
                    realname = row['姓名']
                    password = '111111'
                    user = OAUser(email=email, realname=realname, department=department, status=UserStatusChoices.UNACTIVE)
                    user.set_password(password)
                    users.append(user)
                except Exception:
                    return Response({'detail': '檢查檔案中信箱姓名部門名稱'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # 原子操作
                # 要嘛全部數據創建成功，要嘛全部失敗
                with transaction.atomic():
                    OAUser.objects.bulk_create(users)
            except Exception:
                return Response({'detail': '員工數據添加錯誤'}, status=status.HTTP_400_BAD_REQUEST)

            # 異步給每個新增的員工發送信箱
            for user in users:
                send_active_email(request, user.email)
            return Response()
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({detail: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TestCeleryView(APIView):
    def get(self, request):
        # 用celery異步執行debug_task任務
        debug_task.delay()
        return Response({'detail': 'ok'})