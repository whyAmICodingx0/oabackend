from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models.fields.related import RelatedField
from shortuuidfield import ShortUUIDField

class UserStatusChoices(models.IntegerChoices):
    # 已經啟用的
    ACTIVED = 1
    # 沒有啟用
    UNACTIVE = 2
    # 被鎖定
    LOCKED = 3

class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, realname, email, password, **extra_fields):
        """
        創建用戶
        """
        if not realname:
            raise ValueError("必須設置真實姓名")
        # 信箱標準化
        email = self.normalize_email(email)
        user = self.model(realname=realname, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, realname, email=None, password=None, **extra_fields):
        """
        創建普通員工
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(realname, email, password, **extra_fields)

    def create_superuser(self, realname, email=None, password=None, **extra_fields):
        """
        創建超級員工
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('status', UserStatusChoices.ACTIVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超級用戶必須設置： is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超級用戶必須設置： is_superuser=True.")

        return self._create_user(realname, email, password, **extra_fields)


# 重寫user模型
class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    自定義的USER模型
    """
    uid = ShortUUIDField(primary_key=True)
    realname = models.CharField(max_length=150, unique=False)
    email = models.EmailField(unique=True, blank=False)
    telephone = models.CharField(max_length=20, blank=True)
    # 是否為員工
    is_staff = models.BooleanField(default=True)
    # 只要關注status即可，無須關注is_active
    status = models.IntegerField(choices=UserStatusChoices, default=UserStatusChoices.UNACTIVE)
    is_active = models.BooleanField(default=True)
    # 加入的時間
    date_joined = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey('OADepartment', null=True, on_delete=models.SET_NULL, related_name='staffs', related_query_name='staffs')

    objects = OAUserManager()

    EMAIL_FIELD = "email"
    # USERNAME_FIELD: 是用來做鑑權的，會把authenticate的username參數，傳給USERNAME_FIELD指定的字段
    # from django.contrib.auth import authenticate
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS: 指定那些字段是必須要傳的，但是不能重複包含EMAIL_FIELD和USERNAME_FIELD已經設置過的值
    REQUIRED_FIELDS = ["realname", "password"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.realname

    def get_short_name(self):
        return self.realname

    class Meta:
        ordering = ("-date_joined",)

class OADepartment(models.Model):
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=200)
    # leader
    leader = models.OneToOneField(OAUser, null=True, on_delete=models.SET_NULL, related_name='leader_department', related_query_name='leader_department')
    # manager
    manager = models.ForeignKey(OAUser, null=True, on_delete=models.SET_NULL, related_name='manager_departments', related_query_name='manager_departments')
