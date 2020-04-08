from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager) : # User의 개체 생성은 UserManager 클래스를 사용한다
    def create_user(self, username, password, last_name, email, phone, date_of_birth):
        user = self.model(
            username = username,
            last_name = last_name,
            email = self.normalize_email(email),
            phone = phone,
            date_of_birth = date_of_birth,
            date_joined = timezone.now(),
            is_superuser = 0,
            is_staff = 0,
            is_active = 1
        )

        user.set_password(password) #password는 django의 비밀번호 생성 메소드를 사용한다.
        user.save(using=self._db) #위의 회원정보를 저장, auth_user에 저장된다.

        return user

    def create_superuser(self,username, last_name,email,phone,date_of_birth,password) : #superuser 생성을 위한 메소드
        user = self.create_user(
            username = username,
            last_name = last_name,
            email = email,
            phone = phone,
            date_of_birth = date_of_birth
        )

        user.is_superuser = 1
        user.is_staff = 1
        user.save(using=self._db)

        return user

class User(AbstractBaseUser): # USer 클래스 개체 생성
    password = models.CharField(max_length=128)
    username = models.CharField(unique=True, max_length=150)
    is_superuser = models.IntegerField()
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=254)
    date_of_birth = models.DateTimeField()
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(blank=True,null=True)
    is_staff = models.IntegerField(blank=True,null=True)
    is_active = models.IntegerField(blank=True,null=True)
    first_name = models.CharField(max_length=30,blank=True,null=True)

    objects = UserManager() # User클래스는 사용 시 UserManager 클래스를 사용

    USERNAME_FIELD = 'username' # 사용자 ID로 사용할 필드를 지정
    REQUIRED_FIELDS = ['last_name','phone','email','date_of_birth'] # 필수 입력 필드를 지정

    def has_perm(self, perm, obj=None): #django에서 제공하는 패키지의 회원정보 모델을 사용하여 접근 가능여부 값을 반환
        return True
    
    def has_module_perms(self,app_label): # 위와 동일
        return True

    class Meta: # 회원정보 테이블을 auth_user로 지정한다.
        db_table = 'auth_user'


class BoardCategories(models.Model) :
    category_type = models.CharField(max_length=45)
    category_code = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    category_desc = models.CharField(max_length=100)
    list_count = models.IntegerField(blank=True,null=True)
    authority = models.IntegerField(blank=True,null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_update_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s (%s)' % (self.category_name, self.category_code)
    

    class Meta:
        managed = False # managed를 false로 함으로써 테이블 손실을 방지
        db_table = 'board_categories'

class Boards(models.Model) :
    category = models.ForeignKey(BoardCategories, models.DO_NOTHING) # 외래키를 참조한 다른 모델 클래스를 QuerySet 형태로 지정, 외래키의 값을 쉽게 가져올 수 있다.
    user = models.ForeignKey(User, models.DO_NOTHING)
    title = models.CharField(max_length=300)
    content = models.TextField()
    registered_date = models.DateTimeField(default=timezone.now)
    last_update_date = models.DateTimeField(default=timezone.now)
    view_count = models.IntegerField(blank=True,default=0)
    image = models.ImageField(upload_to="images/%Y/%m/%d", blank=True)

    def __str__(self):
        return '[%d] %.40s' % (self.id, self.title)

    class Meta :
        managed = False
        db_table = 'boards'


class BoardReplies(models.Model):
    article = models.ForeignKey(Boards, models.DO_NOTHING)
    user = models.ForeignKey(User,models.DO_NOTHING)
    level = models.IntegerField(blank=True,null=True)
    content = models.TextField()
    registered_date = models.DateTimeField(default=timezone.now)
    last_update_date = models.DateTimeField(default=timezone.now)
    references_reply_id = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return '[%d] %.40s - [%d] %.40s' % (self.article.id, self.article.title, self.id, self.content)

    class Meta :
        managed = False
        db_table = 'board_replies'

class BoardLikes(models.Model) :
    article = models.ForeignKey(Boards, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    registered_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '[%d] %.40s - %s' % (self.article.id, self.article.title, self.user.last_name)

    class Meta :
        managed = False
        db_table = 'board_likes'



# Create your models here.
