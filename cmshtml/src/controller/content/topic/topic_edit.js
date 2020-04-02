layui.define(['form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,layer = layui.layer
    ,form = layui.form;


    $(document).on('click', '#uploadfileface', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossupload', {'operate':3}).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('faceimg').value = field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                            document.getElementById('img_faceimg').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });
    $(document).on('click', '#uploadfilemain', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossupload', {'operate':3}).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('maininfourl').value = field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
                            document.getElementById('img_maininfourl').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });
    exports('content/topic/topic_edit', {})
});