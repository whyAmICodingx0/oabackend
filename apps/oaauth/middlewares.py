from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse

OAUser = get_user_model()

class LoginCheckMiddleware(MiddlewareMixin):
    keyword = 'JWT'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.white_list = [reverse("oaauth:login"), reverse("staff:active_staff"), reverse("home:health_check")]

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1. 如果返回None，那麼會正常執行
        # 2. 如果返回一個HttpResponse對象，那們不會繼續執行是圖，以及後面的中間鑑
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()
            request.auth = None
            return None
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError('請傳入JWT')

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
                    # django自帶的request
                    request.user = user
                    request.auth = jwt_token
                except:
                    msg = '用戶不存在'
                    raise exceptions.AuthenticationFailed(msg)

            except jwt.ExpiredSignatureError:
                msg = 'token已經過期'
                raise exceptions.AuthenticationFailed(msg)

        except Exception as e:
            print(e)
            return JsonResponse(data={'detail': str(e)}, status=HTTP_403_FORBIDDEN)
