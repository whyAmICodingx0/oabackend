from rest_framework import serializers
from .models import Absent, AbsentStatusChoices, AbsentType
from apps.oaauth.serializers import UserSerializer
from rest_framework import exceptions
from .utils import get_responder

class AbsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentType
        fields = '__all__'

class AbsentSerializer(serializers.ModelSerializer):
    # read_only: 這個參數，只會在ORM模型序列化成字典時將這個字段序列化
    # write_only: 這個參數，只會在data進行校驗的時候才會用到
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responder = UserSerializer(read_only=True)
    class Meta:
        model = Absent
        fields = '__all__'

    # 驗證absent_type_id是否在資料庫存在
    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(id=value).exists():
            raise exceptions.ValidationError('請假類型不存在')
        return value

    # create
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        # 獲取審核者
        responder = get_responder(request)
        # 如果是董事會的leader，請假直接通過
        if responder is None:
            validated_data['status'] = AbsentStatusChoices['PASS']
        else:
            validated_data['status'] = AbsentStatusChoices['AUDITING']
        absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
        return absent

    # update
    def update(self, instance, validated_data):
        if instance.status != AbsentStatusChoices['AUDITING']:
            raise exceptions.APIException(detail='不能修改已經確定的請假數據')
        request = self.context['request']
        user = request.user
        if instance.responder.uid != user.uid:
            raise exceptions.AuthenticationFailed(detail='你無權處理該請假')
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance
