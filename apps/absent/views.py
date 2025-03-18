from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .models import AbsentType, Absent, AbsentStatusChoices
from .serializers import AbsentSerializer, AbsentTypeSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import get_responder
from apps.oaauth.serializers import UserSerializer

# Create your views here.
# 1. 發起考勤(create)
# 2. 處理考勤(update)
# 3. 查看自己考勤列表(list?who=my)
# 4. 查看下屬考勤列表(list?who=sub)
# class AbsentViewSet(viewsets.ModelViewSet):
class AbsentViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer

    def update(self, request, *args, **kwargs):
        # 默認情況下，如果要修改某一條數據，那麼要把這個數據的序列化中指定的字段都上傳
        # 如果想只修改一部份數據，那麼可以在kwargs中設置partial為true
        # 允許部分更新（partial update）
        kwargs['partial'] = True
        # 呼叫 DRF 預設的 update
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            result = queryset.filter(responder=request.user)
        else:
            result = queryset.filter(requester=request.user)

        # result: 代表符合要求的數據
        # pageinage_queryser方法: 會做分頁的邏輯處理
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response: 除了返回序列化後的數據外，還會返回總數據多少，上一頁url是什麼
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(result, many=True)
        return Response(data=serializer.data)

# 1. 請假類型
class AbsentTypeView(APIView):
    def get(self, request):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(types, many=True)
        return Response(serializer.data)

# 2. 顯示省批者
class ResponderView(APIView):
    def get(self, request):
        responder = get_responder(request)
        # serializer: 如果序列化的對象是一個None，那不會抱錯，而是返回一個包含除了主見之外的的所有空字典或默認值
        serializer = UserSerializer(responder)
        return Response(data=serializer.data)