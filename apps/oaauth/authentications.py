import jwt
import time
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from .models import OAUser


def generate_jwt(user):
    timestamp = int(time.time()) + 60*60*24*7
    # 老師版本：因為jwt.encode返回是bytes數據類型，因此需要decode解碼成str類型
    # but現在用已經不用.decode就已經是str類型
    return jwt.encode({"userid":user.pk, "exp":timestamp}, settings.SECRET_KEY)

class UserTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 這裡的request: 是rest_framework.request.Request對象
        # 這裡的對象是針對django的HttpRequest對象進行了封裝
        return request._request.user, request._request.auth

class JWTAuthentication(BaseAuthentication):
    """
    Authorization: JWT 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'JWT'
    model = None

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Authorization 不可用'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Authorization 不可用，應該提供一個空格'
            raise exceptions.AuthenticationFailed(msg)

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
            userid = jwt_info.get('userid')
            try:
                user = OAUser.objects.get(pk=userid)
                setattr(request, 'user', user)
                return (user, jwt_token)
            except:
                msg = '用戶不存在'
                raise exceptions.AuthenticationFailed(msg)

        except jwt.ExpiredSignatureError:
            msg = 'token已經過期'
            raise exceptions.AuthenticationFailed(msg)
