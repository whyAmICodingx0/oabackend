from rest_framework.views import APIView
from apps.inform.models import Inform, InformRead
from apps.inform.serializers import InformSerializer
from django.db.models import Q, Prefetch
from rest_framework.response import Response
from apps.absent.models import Absent
from apps.absent.serializers import AbsentSerializer
from apps.oaauth.models import OADepartment
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class LatestInformView(APIView):
    """
    返回最新的十條通知
    """
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        current_user = request.user
        # 返回公共的，或者是我所在的部門能看到的通知
        inform = Inform.objects.prefetch_related(Prefetch('reads', queryset=InformRead.objects.filter(user_id=current_user.uid)), 'departments').filter(Q(public=True) | Q(departments=current_user.department))[:10]
        serializer = InformSerializer(inform, many=True)
        return Response(serializer.data)


class LatestAbsentView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        # 董事會的人可以看到所有人的請假訊息，非董事會只能看到自己部門的
        current_user = request.user
        queryset = Absent.objects
        if current_user.department.name != '董事會':
            queryset = queryset.filter(requester__department_id=current_user.department_id)
        queryset = queryset.all()[:10]
        serializer = AbsentSerializer(queryset, many=True)
        return Response(serializer.data)

class DepartmentStaffCountView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        rows = OADepartment.objects.annotate(staff_count=Count('staffs')).values('name', 'staff_count')
        print(rows)
        print('='*10)
        return Response(rows)

class HealthCheckView(APIView):
    def get(self, request):
        return Response({"code": 200})