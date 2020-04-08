from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Count
from django.core.paginator import Paginator
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import linebreaksbr
from django.http import JsonResponse   
from .models import *
import datetime
import math

# Create your views here.

def main_page(request):
    return render(request,'main.html')

def user_register_page(request):
    return render(request,'user_register.html')

def user_register_idcheck(request): #ID중복체크 함수 
    if request.method == "POST":
        username = request.POST['username']
    else:
        username = ''

    idObject = User.objects.filter(username__exact=username)
    idCount = idObject.count()

    if idCount > 0 :
        msg = "<font color='red'>이미 존재하는 ID입니다.</font><input type='hidden' name='IDCheckResult' id='IDCheckResult' value=0 />"
    else:
        msg = "<font color='blue'>사용할 수 있는 ID입니다.</font><input type='hidden' name='IDCheckResult' id='IDCheckResult' value=1 />"
    return HttpResponse(msg)

def user_register_result(request):
    if request.method == "POST" :
        username = request.POST['username']
        password = request.POST['password']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        birth_year = int(request.POST['birth_year'])
        birth_month = int(request.POST['birth_month'])
        birth_day = int(request.POST['birth_day'])

    try:
        if username and User.objects.filter(username__exact=username).count() == 0:
            date_of_birth = datetime.datetime(birth_year, birth_month, birth_day)
            
            
            
            user = User.objects.create_user(
                username,password,last_name,email,phone,date_of_birth
            )

            redirection_page = '/boardapp/user_register_completed/'
        else:
            redirection_page = '/boardapp/error/'
    except Exception as e:
            print(e)
            redirection_page = '/boardapp/error/'
            

    return redirect(redirection_page)

def user_register_completed(request):
    return render(request, 'user_register_completed_page.html')

def board_list_page(request, category=''):
    if request.method == 'POST': #게시판 검색 기능
        search_text = request.POST['search_text']
    else:
        search_text= ''
    
    if category: # 카테고리 별 데이터 저장
        articles = Boards.objects.filter(category__category_code=category)
        board_category = BoardCategories.objects.get(category_code=category)
        list_count= board_category.list_count
    else:
        articles = Boards.objects.all()
        board_category = BoardCategories()
        list_count = 10
    
    if search_text: # 검색 조건에 따른 게시물 필터
        articles = articles.filter(title__contains=search_text)

    articles = articles.annotate(like_count=Count('boardlikes', distinct=True),reply_count=Count('boardreplies',distinct=True)).order_by('-id')
    # 게시물에 좋아요, 댓글 수 추가 및 id의 역순으로 정렬

    paginator = Paginator(articles,list_count) #paginator와 page 변수 선언
    try:
        page=int(request.GET['page'])
    except:
        page =  1
    
    articles = paginator.get_page(page) #paginator의 get_page에 의해 변환된 게시물 데이터 저장

    page_count = 10 #게시판 목록 구성
    page_list = []
    first_page = (math.ceil(page/page_count)-1)*page_count+1
    last_page = min([math.ceil(page/page_count)*page_count,paginator.num_pages])
    for i in range(first_page, last_page+1): 
        page_list.append(i)


    args = {} #게시판 목록의 전체 데이터를 저장
    args.update({"articles":articles})
    args.update({"board_category":board_category})
    args.update({"search_text":search_text})
    args.update({"page_list":page_list})

    return render(request, 'board_list.html', args) #템플릿 파일과 args를 통해 render

@login_required # 로그인을 한 회원만 접근 가능
def board_write_page(request,category):
    args={}

    board_category = BoardCategories.objects.get(category_code=category)
    args.update({"board_category":board_category})

    return render(request,'board_write.html',args)

@login_required
def board_write_result(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        category_id = request.POST['category_id']
        try:
            img_file = request.FILES['img_file']
        except:
            img_file = None
    else:
        title = None

    try:
        category = BoardCategories.objects.get(id=category_id)
        if request.user and title and content and request.user.is_superuser >= category.authority :
            article = Boards(category=category, user=request.user, title=title, content=content, image=img_file)
            article.save()
            redirection_page = '/boardapp/board_list/' + category.category_code + '/'

        else:
            redirection_page = 'boardapp/error/'
    except:
        redirection_page = 'boardapp/error/'

    return redirect(redirection_page)

class BoardView(DetailView): #boardview는 detailview를 상속받아 사용한다.
    model = Boards
    template_name = 'board_view.html'

    def dispatch(self,request,pk): # dispatch 메소드를 오버라이딩해 재정의한다
        obj = self.get_object()
        if request.user != obj.user:
            obj.view_count = obj.view_count +1
            obj.save()

        return render(request, self.template_name, {"object": obj})

@login_required
def board_delete_result(request):
    if request.method == "POST":
        article_id = request.POST['article_id']
        referer = request.POST['referer']
    else:
        article_id = -1
    
    args={}

    article = Boards.objects.get(id=article_id)

    if request.user == article.user:
        article.delete()

        if referer == "board":
            redirection_page = '/boardapp/board_list/' + article.category.category_code + '/'

        else:
            redirection_page = '/boardapp/comm_list/' + article.category.category_code + '/'

    else:
        redirection_page = '/boardapp/error/'
    
    return redirect(redirection_page)

class BoardModifyView(DetailView):
    model = Boards 
    template_name = 'board_modify.html'

@login_required
def board_modify_result(request):
    if request.method == "POST" :
        title = request.POST['title']
        content = request.POST['content']
        article_id = request.POST['id']
        referer = request.POST['referer']
        try:
            img_file = request.FILES['img_file']
        except:
            img_file = None
    else:
        title = None
    
    args= {}
    

    try:
        if request.user and title and content and article_id:
            article = Boards.objects.get(id=article_id)

            if article.user != request.user:
                redirection_page = '/boardapp/error/'
            else:
                article.title = title
                article.content = content
                article.last_update_date = timezone.now()

                if img_file:
                    article.image = img_file
                
                article.save()

                if referer == 'board':                   
                    redirection_page = '/boardapp/board_view/' + str(article.id) + '/'
                    
                else:
                    redirection_page = '/boardapp/comm_view/' + str(article.id) + '/'
        else:
            redirection_page = '/boardapp/error/'
    
    except Exception as e:
        print(e)
        redirection_page='/boardapp/error/'   
    return redirect(redirection_page)

def board_comm_list_page(request, category): #일반 게시판과 달리 category를 파라미터로 받아 사용한다.
    error_flag = False #게시판 글쓰기 오류 처리를 위한 변수
    
    # 대화형 게시판 글쓰기
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        try:
            img_file = request.FILES['img_file']
        except:
            img_file = None

        try:
            board_category = BoardCategories.objects.get(category_code=category)

            if request.user and title and content and request.user.is_superuser >= board_category.authority :
                article = Boards(category=board_category, user=request.user, title=title, content=content, image=img_file)
                article.save()
            else:
                error_flag =True
        except: 
            error_flag=True
    
    
    # 대화형 게시판 목록
    articles = Boards.objects.filter(category__category_code=category).order_by('-id')
    board_category = BoardCategories.objects.get(category_code=category)
    paginator = Paginator(articles,board_category.list_count)
    

    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1
    
    articles = paginator.get_page(page)
    

    page_count = 10
    page_list = []
    first_page = (math.ceil(page/page_count)-1)*page_count+1
    last_page = min([math.ceil(page/page_count)*page_count,paginator.num_pages])
    for i in range(first_page, last_page+1): 
        page_list.append(i)
    
    args={}
    args.update({"error_flag":error_flag})
    args.update({"articles":articles})
    args.update({"board_category":board_category})
    args.update({"page_list":page_list})
    
    
    return render(request, 'board_comm_list.html', args)

class BoardCommView(DetailView):
    model = Boards 
    template_name = 'board_comm_view.html'


class BoardCommModifyView(DetailView):
    model = Boards 
    template_name = 'board_comm_modify.html'


def reply_write_result(request) :
    if request.method == "POST" :
        content = request.POST['content']
        level = request.POST['level']
        id = request.POST['id']
        print(content, level, id)
    else :
        content = None

    try:
        if request.user and content and id:
            if level == "0":
                article = Boards.objects.get(id=id)
                reply= BoardReplies(article=article, user=request.user, level=level, content=content)
                reply.save()
                reply.references_reply_id = reply.id #신규 댓글을 입력할 때에는 댓글ID가 결정되지 않아 Reference_reply_id를 입력할 수 없음, 그래서 save 후 reference 입력
                reply.save()
                redirection_page = '/boardapp/reply_list/' + id + '/'

            else:
                article = BoardReplies.objects.get(id=id).article
                reply = BoardReplies(article=article, user=request.user, level=level, content=content, references_reply_id=id)
                reply.save()
                redirection_page='/boardapp/reply_list/' + str(article.id) + '/'
        else:
                redirection_page = '/boardapp/error1/'
    
    except Exception as e :
        print(e)
        redirection_page='boardapp/error/'

    return redirect(redirection_page)

def reply_list(request, article):
    replies = BoardReplies.objects.filter(article__id=article).order_by('-references_reply_id','level','-id')
    args={}
    args.update({"replies":replies})
    return render(request, 'reply_list.html',args)

class ReplyModifyView(DetailView):
    model = BoardReplies
    template_name = 'reply_modify.html'

def reply_modify_result(request):
    if request.method == "POST":
        content = request.POST['content']
        reply_id = request.POST['id']
    else:
        content = None

    try:
        if request.user and content and reply_id:
            reply = BoardReplies.objects.get(id=reply_id)     
            reply.content = content   
            reply.save()
            redirection_page = '/boardapp/reply_list/' + str(reply.article.id) + '/'

        else:
            redirection_page = '/boardapp/error1/'
    except:
        redirection_page = '/boardapp/error2/'

    
    return redirect(redirection_page)

@login_required
def reply_delete_result(request):
    try:
        if request.method == "POST":
            reply_id = request.POST['id'] #버그 수정 : replyDeleteClick에서 전달하는 인자 이름이 "id" 이므로 request.POST의 인자도 같이 맞춰야 한다. 
        else:
            reply_id = -1 #POST가 아닐 시 무효화
    
        reply = BoardReplies.objects.get(id=reply_id) # id가 일치하는(불러올) 쿼리셋 생성
       

        if request.user == reply.user:
            reply.delete()
            redirection_page = '/boardapp/reply_list/' + str(reply.article.id) + '/'

        else:
            redirection_page = '/boardapp/error/'
    except Exception as e:
        print(e)
        redirection_page= '/boardapp/error2/'
    return redirect(redirection_page)

def board_like(request,article):
    args={} 

    like_count = BoardLikes.objects.filter(article__id=article).count()
    user_count = BoardLikes.objects.filter(article__id=article).filter(user=request.user).count()

    args.update({"like_count": like_count})
    args.update({"user_count": user_count})
    args.update({"article_id": article})

    return render(request, 'board_like.html' ,args)

def board_like_result(request):
    if request.method == "POST":
        article_id = request.POST['article_id']
    else:
        article_id = -1

    article = Boards.objects.get(id=article_id)
    like_confirm = BoardLikes.objects.filter(article=article)
    like_already_chk = like_confirm.filter(user=request.user).count()

    args={}
    if article.user == request.user:
        args.update({"like_err_msg":"본인의 게시물에는 추천할 수 없습니다."})
    elif like_already_chk == 1:
        args.update({"like_err_msg":"이미 추천한 게시물입니다."})
    else:
        boardlike = BoardLikes(article=article, user=request.user)
        boardlike.save()

    args.update({"article_id":article_id})

    return JsonResponse(args)

def main_page(request):
    articles = Boards.objects.all()
    list_count = 10

    articles = articles.annotate(like_count=Count('boardlikes',distinct=True),
    reply_count=Count('boardreplies',distinct=True)).order_by('-id')[:list_count]

    args={}
    args.update({"articles":articles})

    return render(request,'main.html', args)

def introduce_page(request):

    return render(request,'introduce.html')

def error_page(request):

    return render(request,'error.html')
 
