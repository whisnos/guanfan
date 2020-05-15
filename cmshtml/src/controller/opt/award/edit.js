layui.define(['form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,layer = layui.layer
    ,form = layui.form;

    $(document).on('click', '#uploadfile_openprize', function(){
        admin.popup({
            title: '上传开奖按钮'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-award-oss-fileupload-openimg'
            ,success: function(layero, index){
                updata_set = {
                    'spaceid':document.getElementById('id').value,
                    'operate':7,
                    'filename':"main/openprize" + new Date().getTime() + ".png"
                }; //operate 上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 活动 8 其它
                view(this.id).render('app/common/ossuploadspace', updata_set).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log("开奖:", field);
                        if(field.cmsupfiles != ''){
                            document.getElementById('openimgshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1) + "?" + Math.random().toString(); // 更新食谱图片文件地址
                            document.getElementById('openimg').value = field.cmsupfiles.slice(0,-1);
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });

    $(document).on('click', '#uploadfile_joinbutton', function(){
        admin.popup({
            title: '上传参与按钮'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-award-oss-fileupload-joinimg'
            ,success: function(layero, index){
                updata_set = {
                    'spaceid':document.getElementById('id').value,
                    'operate':7,
                    'filename':"main/join" + new Date().getTime() + ".png"
                }; //operate 上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 活动 8 其它
                view(this.id).render('app/common/ossuploadspace', updata_set).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段                       
                        if(field.cmsupfiles != ''){
                            // $("#joinimgshow").attr("src", layui.setter.basehost + field.cmsupfiles.slice(0,-1) + "?" + Math.random().toString())
                            document.getElementById('joinimgshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1) + "?" + Math.random().toString(); // 更新食谱图片文件地址
                            document.getElementById('joinimg').value = field.cmsupfiles.slice(0,-1);
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });

    $(document).on('click', '#uploadfile_mainimg', function(){
        admin.popup({
            title: '上传奖品图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-award-oss-fileupload-mainimg'
            ,success: function(layero, index){
                updata_set = {
                    'spaceid':document.getElementById('id').value,
                    'operate':7,
                    'filename':"main/awardmain" + new Date().getTime() + ".jpg"
                }; //operate 上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 活动 8 其它
                // console.log(updata_set);
                view(this.id).render('app/common/ossuploadspace', updata_set).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段
                        // console.log(field);
                        if(field.cmsupfiles != ''){
                            // console.log(layui.setter.basehost + field.cmsupfiles.slice(0,-1), document.getElementById('mainimgshow'));
                            document.getElementById('mainimgshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1) + "?" + Math.random().toString(); // 更新食谱图片文件地址
                            document.getElementById('mainimg').value = field.cmsupfiles.slice(0,-1);
                        }
                        layer.close(index); //执行关闭 
                    });
                });
            }
        });
    });

    exports('opt/award/edit', {})
});