
function writeSend() {
    
    if (!$('#title').val())
    {
        alert("제목을 입력해 주시기 바랍니다.");
        return;
    }

    if (!$('#content').val())
    {
        alert("글 내용을 입력해 주시기 바랍니다.");
        return;
    }

    $('#write_form').submit();
}

function deleteClick(id) { //delete는 일반,대화형 게시판 공통으로 사용, id파라미터의 유무를 통해 게시판 유형을 구분한다.
    if (confirm("정말 삭제하시겠습니까?"))
    {
        if(!id)
        {
            $('#delete_form').submit();
        } else {
            $("form[data-id="+id+"]").submit();
        }
    }
}

function modifySend() {
    if (!$('#title').val())
    {
        alert("제목을 입력해 주시기 바랍니다.");
        return;
    }

    if (!$('#content').val())
    {
        alert("수정할 글 내용을 입력해 주시기 바랍니다.");
        return;
    }

    $('#modify_form').submit();
}

$(document).ready(function() { //특정 템플릿파일을 특정 태그(article.id)의 html로 나타내기
    $('.article-view').each(function() {
        var article_id = $(this);
        $.ajax({
            type: "GET",
            url: "/boardapp/comm_view/" + $(this).data('id'),
            success: function(response) {
                article_id.html(response);
            },
        });
    });
});



function modifyCommSend(id) {
    var article_div = 'input[name=modify_title]'; //수정 후 처리 완료 표시할 div를 지정하기 위한 변수, 해당 article-view+id를 지정한다.
    var article_form = 'form[name=modify_form]'; //해당 form+id의 form을 지정하기 위한 변수

    if (!$( article_div ).val()) // 게시물 검증(제목,내용)
    {
        alert("제목을 입력해 주시기 바랍니다.");
        return;
    }

    if (!$('textarea[name=modify_content]').val())
    {
        alert("수정할 글 내용을 입력해 주시기 바랍니다.");
        return;
    }

    var data = new FormData($(article_form)[0]); //form에서 입력된 데이터를 data변수에 저장
    
    data.append("img_file",$('input[name=img_file]')[0].files[0]); //이미지를 data에 덧붙임 (type=file로 붙임)

    $.ajax({
        type: "POST",
        url: "/boardapp/board_modify_res/",
        processData: false,
        contentType: false,
        data:data,
        success: function(response) {
            $(".article-view[data-id="+id+"]").html(response); //article_div 변수에 해당하는 화면 영역에 템플릿을 표시한다.
        },
    });
}

function modifyCancle(id) {
    $.ajax({
        type:"GET",
        url:"/boardapp/comm_view/"+id,
        success: function(response) {
            $(".article-view[data-id="+id+"]").html(response);
        },
    });
}

function modifyClick(id) {
    $.ajax({
        type: "GET",
        url: "/boardapp/comm_modify/" + id,
        success: function(response) {
            $(".article-view[data-id="+id+"]").html(response);
        },
    });
}

function replyShow(id) {
    $.ajax({
        url : "/boardapp/reply_list/" + id,
        dataType : "html",
        type : "get",  // post 또는 get
        data : id,   // 호출할 url 에 있는 페이지로 넘길 파라메터
        success : function(result){
            $("div[name='reply_div']").html(result);
        },
    });

}

function replyWriteSend(id) {
    // var reply_div = '.article-reply[data-id='+id+']';
    // var reply_form = 'form[data-type=reply][data-id='+id+']';

    if (!$('textarea[textarea-id='+id+']').val())
        {
            alert("댓글 내용을 입력해 주시기 바랍니다.");
            return;
        }

        $.ajax({
            type: "POST",
            url: "/boardapp/reply_write_res/",
            data:$("form[name='reply_form']").serialize(),
            success: function(response) {
                $("div[name='reply_div']").html(response); // reply_div에 댓글 결과 html 전송
                $('textarea[textarea-id='+id+']').val(''); //전송 후 textarea 초기화
            },
        });
}

function replyClick(reply_id) {
    $('.reply-reply').each(function() {
        $(this).css('display','none');
    });

    $('.reply-reply[data-id='+reply_id+']').css('display','block');
}

function replyReplySend(id, article_id) {
    
    // var reply_div = '.article-reply[data-id='+id+']';
    // var reply_form = 'form[data-type=reply][data-id='+id+']';

    if (!$('textarea[data-id='+id+']').val())
        {
            alert("대댓글 내용을 입력해 주시기 바랍니다.");
            return;
        }

        $.ajax({
            type: "POST",
            url: "/boardapp/reply_write_res/",
            data:$('form[data-id='+id+']').serialize(),
            success: function(response) {
                $("div[name='reply_div']").html(response); // reply_div에 댓글 결과 html 전송
                $('textarea[data-id='+id+']').val(''); //전송 후 textarea 초기화
                $('.reply-reply[data-id='+id+']').css('display','none')
            },
        });
}

function replyModifyClick(id) {
    $.ajax({
        type:"GET",
        url: "/boardapp/reply_modify/"+id,
        success: function(response) {
            $('div[name="reply_block"]div[data-id='+id+']').html(response);
        },
    });
}

function replyModifySend(id, article_id) {

    if (!$('textarea[data-id='+id+']').val())
    {
        alert("수정할 댓글 내용을 입력해 주시기 바랍니다.")
        return;
    }


    $.ajax({
        type:"POST",
        url: "/boardapp/reply_modify_res/",
        data: $('form[data-id='+id+']form[data-type="reply-modify"]').serialize(), //버그 수정- form 위치를 data-id로만 X, data-type으로 세분화해야 content가 올바로 전송
        header:{"Content-Type":"false"},
        success: function(response) {
            $("div[name='reply_div']").html(response);
            $('form[data-id='+id+']').val('');
        },
    });
}

function replyDeleteClick(id, article_id) {
    if (confirm("댓글을 삭제하시겠습니까?"))
    {
        $.ajax({
            type:"POST",
            url: "/boardapp/reply_delete_res/",
            data: $('form[data-type="reply_delete"],form[data-id='+id+']').serialize(), //버그 수정, querySelector에 "," 넣어서 다중선택
            success: function(response) {
                $("div[name='reply_div']").html(response);
                $('textarea[textarea-id='+id+']').val('');
            },
        });
    }
}

var inProgress = false;

function likeClick(article_id) {
    var like_form= 'form[data-type="like"],form[data-id='+article_id+']';

    if(!inProgress) {
        inProgress = true; //추천진행이 false인 경우 true로 변경

        $.ajax({
            type: "POST",
            url: "/boardapp/board_like_res/", //최종적으로 POST를 통해 board_like_res 전송
            success: function(response) { //error가 뜬 경우 경고 메세지 출력
                if (response.like_err_msg) {
                    alert(response.like_err_msg);
                }
                $.ajax({ //추천을 진행
                    type: "GET",
                    url: "/boardapp/board_like/" + response.article_id,
                    success: function(response) {
                        $('.article-like[data-id='+article_id+']').html(response);
                    },
                });
                inProgress = false; //추천이 끝나고 추천진행을 다시 false로 변경
            },
        });
    }
}

