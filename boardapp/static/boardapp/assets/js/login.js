$(document).ready(function() { //enter를 누를시 submit이 되게 하는 함수
    $('input').keydown(function(e) {
        if (e.which == 13)
        {
            $('form').submit();
        }
    });
});

function login() {
    if (!$('#username').val()) 
        {
            alert("아이디를 입력해 주시기 바랍니다.");
            return;
        }
    if (!$('#password').val()) {
        alert("비밀번호를 입력해 주시기 바랍니다.");
        return;
    }

    $('#login_form').submit();

}