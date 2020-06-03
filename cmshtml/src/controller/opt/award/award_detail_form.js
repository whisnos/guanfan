layui.define(['form','table'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,table = layui.table
    ,view = layui.view
    ,form = layui.form;
    form.render(null, 'cms-award-form');

    $(document).on('click', '#uploadfileawarddetailedit', function(){
        admin.popup({
            title: '上传奖品详情图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-oss-fileupload-award-detail'
            ,success: function(layero, index){
                data = {'operate':2, 'spaceid': document.getElementById('detailuserid').value, 'filename':''};
                //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                console.log(data, 2323232322323);
                view(this.id).render('app/common/ossuploadspace',data).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){

                        var field = data.field; //获取提交的字段
                        console.log(field);
                        if(field.cmsupfiles != ''){
                            document.getElementById('image').value = field.cmsupfiles.slice(0,-1); // 更新奖品详情图片文件地址
                            document.getElementById('image').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址

                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });
    exports('opt/award/award_detail_form', {})
});