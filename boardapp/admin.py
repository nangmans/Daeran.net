from django.contrib import admin
from boardapp.models import *

# Register your models here.

class BoardsAdmin(admin.ModelAdmin): #list의 object를 ID와 Title로 볼 수 있게끔 해주는 class
    list_display = ('id','title')

admin.site.register(Boards, BoardsAdmin) #boards의 object들은 위의 클래스 정의에 따라 id와 title을 볼 수 있다.
admin.site.register(BoardReplies)
admin.site.register(BoardLikes)
admin.site.register(BoardCategories)
admin.site.register(User)




