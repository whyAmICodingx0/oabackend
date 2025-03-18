from rest_framework import serializers
from django.core.validators import FileExtensionValidator, get_available_image_extensions

class UploadImageSerializer(serializers.Serializer):
    # ImageField: 會校驗上傳的文件是否是圖片
    # .png/.jpeg/.jpg
    image = serializers.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        error_messages={'required': '請上傳圖片', 'invalid_image': '請上傳正確格式的圖片'}
    )
    def validate_image(self, value):
        # 圖片大小單位是字節
        # 1024B: 1KB ， 1024KB: 1MB
        # 以下單位是B
        max_size = 0.5 * 1024 * 1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError('圖片最大不能超過0.5MB')
        return value