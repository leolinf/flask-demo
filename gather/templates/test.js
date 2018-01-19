// 登陆
function loginAjax(param) {
    var self = this;
    $.ajax({
        type: 'post',
        url: '/user/login',
        dataType: 'json',
        data: param,
        success: function(data) {

        },
        error: function(error) {
        console.log(error);
        }
    })
}
