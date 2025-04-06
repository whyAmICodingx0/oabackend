from rest_framework import serializers
from .models import OAUser, UserStatusChoices, OADepartment
from rest_framework import exceptions


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={'required': '請輸入信箱'})
    password = serializers.CharField(max_length= 20, min_length=6)

    # 驗證方法復寫
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError('請輸入正確的信箱')
            if not user.check_password(password):
                raise serializers.ValidationError('密碼錯誤')
            if user.status == UserStatusChoices.UNACTIVE:
                raise serializers.ValidationError('用戶未被啟用')
            elif user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError('用戶已經被鎖定')
            # 為了節省查找SQL次數，這裡把user直接放到attrs中
            attrs['user'] = user
        else:
            raise serializers.ValidationError('請輸入信箱和密碼')
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = OAUser
        # fields = '__all__'
        exclude = ('password', 'groups', 'user_permissions')

class ResetPwdSerializer(serializers.Serializer):
    oldpwd = serializers.CharField(max_length= 20, min_length=6)
    pwd1 = serializers.CharField(max_length= 20, min_length=6)
    pwd2 = serializers.CharField(max_length= 20, min_length=6)

    def validate(self, attrs):
        oldpwd = attrs['oldpwd']
        pwd1 = attrs['pwd1']
        pwd2 = attrs['pwd2']

        user = self.context['request'].user
        if not user.check_password(oldpwd):
            raise exceptions.ValidationError('舊密碼錯誤')
        if pwd1 != pwd2:
            raise exceptions.ValidationError('兩個密碼不一樣')
        return attrs