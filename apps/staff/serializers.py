from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

OAUser = get_user_model()


class AddStaffSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=20, error_messages={"required": "請輸入真實姓名！"})
    email = serializers.EmailField(error_messages={"required": "請輸入信箱！", "invalid": "請輸入正確格式的信箱！"})
    password = serializers.CharField(max_length=20, error_messages={"required": "請輸入密碼！"})

    def validate(self, attrs):
        request = self.context.get('request')
        email = attrs.get('email')
        # 1. 驗證信箱是否存在
        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('該信箱已經存在')

        # 2. 驗證當前用戶是否為部門的leader
        if request.user.department.leader.uid != request.user.uid:
            raise serializers.ValidationError('非部門leader不能添加員工')
        return attrs


class ActiveStaffSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={"required": "請輸入信箱！", "invalid": "請輸入正確格式的信箱！"})
    password = serializers.CharField(max_length=20, error_messages={"required": "請輸入密碼！"})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = OAUser.objects.filter(email=email).first()
        # if user.status == 1:
        #     raise serializers.ValidationError('帳號已啟用')
        # if user.status == 3:
        #     raise serializers.ValidationError('帳號無法啟用')
        if not user or not user.check_password(password):
            raise serializers.ValidationError('信箱或密碼錯誤')
        attrs['user'] = user
        return attrs


class StaffUploadSerializers(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(['xlsx', 'xls'])],
                                 error_messages={'required': '請上傳excel檔'})
