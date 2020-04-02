layui.define(['form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,layer = layui.layer
    ,form = layui.form;

    $(document).on('click', '#uploadfile_contentimg', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-recommend-campaign-content-oss-fileupload-contentimg'
            ,success: function(layero, index){
                updata_set = {
                    'spaceid': document.getElementById('campaignid').value,
                    'operate':7,
                    'filename': "content/" + new Date().getTime() + ".jpg"
                }; //operate 上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 活动 8 其它
                view(this.id).render('app/common/ossuploadspace', updata_set).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段
                        if(field.cmsupfiles != ''){
                            document.getElementById('contentimgshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
                            document.getElementById('imgurl').value = field.cmsupfiles.slice(0,-1);
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });
    exports('recommend/campaign/contentedit', {})
});