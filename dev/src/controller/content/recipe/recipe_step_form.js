layui.define(['form','table'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,table = layui.table
    ,view = layui.view
    ,form = layui.form;
    form.render(null, 'cms-recipe-form');

    $(document).on('click', '#uploadfile', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossupload', data).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('faceimg').value = field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
          });
      });

    exports('content/recipe/recipe_step_form', {})
});