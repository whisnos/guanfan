layui.define(['table', 'form'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,table = layui.table
    ,view = layui.view
    ,form = layui.form;
    // form.render();
    form.render(null, 'cms-user-verify-form');
 
    //监听提交
    form.on('submit(cms-user-verify-form-submit)', function(data){
        // 认证通过
        var field = data.field;
        // console.log(field);
        field.verify = 1;
        user_check_verify(field);
        // form.render(null, 'cms-user-verify-form');
        table.reload('LAY-cms-user-list');
        layer.close(layer.index); //执行关闭
    });

    //监听提交
    form.on('submit(cms-user-verify-form-denied-submit)', function(data){
        // 认证不通过
        var field = data.field;
        field.verify = 0;
        user_check_verify(field);
        // form.render(null, 'cms-user-verify-form');
        table.reload('LAY-cms-user-list');
        layer.close(layer.index); //执行关闭
    });


    function user_check_verify(data){
        //认证是否通过
        admin.req({
            type: 'post',
            url: '/api/user/checkverify', //认证状态
            data: data,
            success: function (result) {
                if (result.success) {
                    // table.render(null, 'LAY-cms-user-list');
                } else {
                    layer.msg(result.msg)
                }
            },
            error: function (error) {
            }
        });
    }
    layui.use('form', function(){
        form.render();
    }); 
    exports('user/verifyform', {})
});