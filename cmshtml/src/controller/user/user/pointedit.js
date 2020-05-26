layui.define(['table', 'form'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,table = layui.table
    ,view = layui.view
    ,form = layui.form;
    // form.render();
    form.render(null, 'cms-user-verify-form');
 
    //监听提交
    form.on('submit(cms-user-point-form-submit)', function(data){
        // 增加账户积分
        var field = data.field;
        // field.point = 0;
        if(field.point === ''){
            user_add_point({'id':field.id,'point':field.point, 'grade_no':field.grade_no, 'bill_type': 6});
        }else{
            user_set_point({'id':field.id,'point':field.point, 'grade_no':field.grade_no, 'bill_type': 6});
        }
        // form.render(null, 'cms-user-verify-form');
        table.reload('LAY-cms-user-list');
        layer.close(layer.index); //执行关闭
    });

    form.on('submit(cms-user-point-form-decline-submit)', function(data){
        // 扣减账户积分
        var field = data.field;
            if(field.point != ''){
                if(parseInt(field.point) < parseInt(field.grade_no) ){
                    layer.msg('扣减积分无法大于现有积分，请调整')
                }else{
                    user_set_point({'id':field.id,'point': field.point, 'grade_no':field.grade_no, 'bill_type': -3});
                }
            }else{
                layer.msg('积分不存在，请先添加后再扣减', {
                    time: 5000
                });
                layer.msg('积分不存在，请先添加后再扣减', {
                 icon: 1,
                 time: 2000 //2秒关闭（如果不配置，默认是3秒）
                }, function(){
                    table.reload('LAY-cms-user-list');
                    layer.close(layer.index); //执行关闭
                });
                return false;
            }
        // form.render(null, 'cms-user-verify-form');
        table.reload('LAY-cms-user-list');
        layer.close(layer.index); //执行关闭
    });



  function user_set_point(data,index){
      // 添加动态
      admin.req({
          type: 'post',
          url: '/api/user/pointedit', //添加
          data: data,
          success: function (result) {
              if (result.success) {
                  // layer.msg('成功')
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              layer.close(index);
              table.reload('LAY-cms-user-list');
          },
          error: function (error) {
          }
      });
    };

  function user_add_point(data,index){
      // 添加动态
      admin.req({
          type: 'post',
          url: '/api/user/pointadd', //添加
          data: data,
          success: function (result) {
              if (result.success) {
                  // layer.msg('成功')
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              layer.close(index);
              table.reload('LAY-cms-user-list');
          },
          error: function (error) {
          }
      });
    };
    layui.use('form', function(){
        form.render();
    }); 
    exports('user/user/pointedit', {})
});