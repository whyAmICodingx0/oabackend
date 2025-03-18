from rest_framework import status
from rest_framework.views import APIView
from .serializers import UploadImageSerializer
from rest_framework.response import Response
from shortuuid import uuid
import os
from django.conf import settings


class UploadImageView(APIView):
    def post(self, request):
        # 1. 圖片是xx.png，如果用某種手段 xx.py -> xx.png，不給過
        # 2. .png/.jpg/.jpeg, .txt/.py 部接收
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            # abc.png => rege9oggifdk + '.png'
            # os.path.splitext('abc.png') = ('abc', '.png')
            filename = uuid() + os.path.splitext(file.name)[-1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path, 'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)
            except Exception:
                return Response({
                    "errno": 1,
                    "message": "圖片保存失敗"
                })
            file_url = settings.MEDIA_URL + filename
            return Response({
                "errno": 0,
                "data": {
                    "url": file_url,
                    "alt": "",
                    "href": file_url
                }
            })
        else:
            print(serializer.errors)
            print(type(serializer.errors))
            return Response({
                'errno': 1,
                'message': list(serializer.errors.values())[0][0]
            })
