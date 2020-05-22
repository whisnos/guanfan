layui.define(['form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,layer = layui.layer
    ,form = layui.form;

    $(document).on('click', '#uploadfileawardimg', function(){
        admin.popup({
            title: '上传频道图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2, 'spaceid':document.getElementById('awardid').value, 'filename':''};
                //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                // console.log(data);
                // view(this.id).render('app/common/ossupload',data).done(function(){
                    // form.render(null, 'layuiadmin-app-oss-fileupload');

                view(this.id).render('app/common/ossuploadspace',data).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('front_image').value = field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
                            document.getElementById('front_imageshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });

    exports('opt/award/edit', {})
});