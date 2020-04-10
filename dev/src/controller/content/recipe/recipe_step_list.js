layui.define(['table', 'layer', 'form'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,table = layui.table
    ,form = layui.form
    ,layer = layui.layer;
    

    // var router = layui.router();
    // recipeid=router.search.recipeid;
    // recipename=decodeURIComponent(router.search.recipename);
    // recipeid = $('#recipe_for_step_id').val();
    // recipename = "食谱";

    layui.data.handler_content_recipe_list_table = function (params) {
        //食谱步骤列表
        layui.use(['table'], function () {
            var table = layui.table;
            table.render({
                elem: '#LAY-cms-recipe-step-list'
                ,url: '/api/recipestep/list' //获取数据接口
                //,method: "post"
                ,where:{"recipeid":params.id}
                ,cols: [[
                    {type: 'checkbox', fixed: 'left'}
                    // ,{field: 'id', width: 100, title: 'id', sort: true}
                    ,{field: 'sort', width: 100, title: '排序', sort: true}
                    ,{field: 'stepimg', title: '步骤图片', templet:'#recipe_step_img_ViewTpl', width: 100, align: 'center'}
                    ,{field: 'description', title: '步骤描述', minWidth: 400, minHeight:250}
                    ,{title: '操作', width: 200, align: 'center', fixed: 'right', toolbar: '#table-recipe-step-content-list'}
                ]]
                ,page: false
                ,limit: 100
                ,limits: [100, 150, 200, 250, 300]
                ,text: '对不起，加载出现异常！'
            });

            //监听工具条
            table.on('tool(LAY-cms-recipe-step-list)', function(obj){
                var data = obj.data;
                if(obj.event === 'recipe_step_del'){
                    layer.confirm('确定删除此步骤？', function(index){
                        recipe_step_del({'id':obj.data.id});
                        obj.del();
                        layer.close(index);
                    });
                } else if(obj.event === 'recipe_step_edit'){
                    admin.popup({
                        title: '编辑步骤'
                        ,area: ['750px', '550px']
                        ,id: 'LAY-popup-content-recipe-step-edit'
                        ,success: function(layero, index){
                            view(this.id).render('app/content/recipe/steplistform', data).done(function(){
                                form.render(null, 'cms-recipe-step-form');
                            //监听提交
                                form.on('submit(cms-recipe-step-form-submit)', function(data){
                                    var field = data.field; //获取提交的字段
                                    // console.log(field)
                                    //提交 Ajax 成功后，关闭当前弹层并重载表格  
                                    //$.ajax({});
                                    recipe_step_edit(field)
                                    layer.close(index); //执行关闭 
                                });
                            });
                        }
                    });
                } else if(obj.event === 'step_checkbig'){
                    // console.log(obj)
                    var imgurl = '';
                    var origin_img = obj.data.stepimg;
                    // origin_img = origin_img.toLocaleLowerCase();
                    if(origin_img.startsWith('http')){
                        imgurl = origin_img;
                    }else{
                        imgurl = layui.setter.basehost + obj.data.stepimg;
                    }
                    // 查看大图
                    layer.open({
                    title:'查看大图'
                    ,type: 1
                    ,shadeClose: true
                    ,area: ['auto', 'auto']
                    ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
                    });
                }
            });
        });
    }
    function recipe_step_add(data){
        //增加食谱步骤
        admin.req({
            type: 'post',
            url: '/api/recipestep/add', //食谱步骤增加
            data:data,
            success: function (result) {
                if (result.success) {
                    form.render();
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recipe-step-list');
            },
            error: function (error) {
            }
        });
    }

    function recipe_step_del(data){
        //删除食谱步骤
        admin.req({
            type: 'post',
            url: '/api/recipestep/del', //食谱步骤删除
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recipe-step-list');
            },
            error: function (error) {
            }
        });
    }
    
    function recipe_step_edit(data){
        //编辑食谱步骤
        admin.req({
            type: 'post',
            url: '/api/recipestep/edit', //食谱步骤编辑
            data: data,
            success: function (result) {
                if (result.success) {
                    form.render();
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recipe-step-list');
            },
            error: function (error) {
            }
        });
    }

    var active = {
        step_batchdel: function(){
          var checkStatus = table.checkStatus('LAY-cms-recipe-step-list')
          ,checkData = checkStatus.data; //得到选中的数据
          if(checkData.length === 0){
            return layer.msg('请选择数据');
          }
        
          layer.confirm('确定删除吗？', function(index) {
            $.each(checkData, function (index, item) {
              let data = {};
              data['id'] = item.id;
              recipe_step_del(data);
            });
            
            //执行 Ajax 后重载
            /*
            admin.req({
              url: 'xxx'
              //,……
            });
            */
            
            layer.msg('已删除');
          });
        }

        //添加
        ,step_add: function(othis){
          admin.popup({
            title: '添加步骤'
            ,area: ['750px', '550px']
            ,id: 'LAY-cms-content-add'
            ,success: function(layero, index){
              view(this.id).render('app/content/recipe/steplistform').done(function(){
                form.render(null, 'cms-recipe-step-form');
                //监听提交
                // {"id":recipeid}
                form.on('submit(cms-recipe-step-form-submit)', function(data){
                  var field = data.field; //获取提交的字段
                  field.id = $("#recipe_for_step_id").val();
                  console.log(field);
                  //提交 Ajax 成功后，关闭当前弹层并重载表格
                  //$.ajax({});
                  recipe_step_add(field);
                  layer.close(index); //执行关闭 
                });
              });
            }
          });
        }
    }; 
  

    $('.layui-btn.layuiadmin-btn-list').on('click', function(){
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
      });

    // $(document).on('click', '#uploadfilerecipestep', function(){
    //     admin.popup({
    //         title: '上传图片'
    //         ,area: ['550px', '450px']
    //         ,id: 'LAY-popup-content-oss-fileupload'
    //         ,success: function(layero, index){
    //             data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
    //             view(this.id).render('app/common/ossupload', {'operate':2}).done(function(){
    //                 form.render(null, 'layuiadmin-app-oss-fileupload');
    //                 //文件上传,监听关闭
    //                 form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
    //                     var field = data.field; //获取提交的字段
    //                     console.log(field)
    //                     if(field.cmsupfiles != ''){
    //                         document.getElementById('stepimg').value = field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
    //                     }
    //                     layer.close(index); //执行关闭 
    //                 });
    //             });
    //         }
    //     });
    // });
    $(document).on('click', '#uploadfilerecipestep', function(){
        admin.popup({
            title: '上传步骤图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload-recipe-step'
            ,success: function(layero, index){
                data = {'operate':2, 'spaceid': document.getElementById('stepuserid').value, 'filename':''}; 
                //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                console.log(data);
                view(this.id).render('app/common/ossuploadspace',data).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        // var field = data.field; //获取提交的字段
                        // console.log(field)
                        // if(field.cmsupfiles != ''){
                        //     document.getElementById('faceimg').value = field.cmsupfiles.slice(0,-1); // 更新食谱图片文件地址
                        //     document.getElementById('faceimgshow').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        // }
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('stepimg').value = field.cmsupfiles.slice(0,-1); // 更新食谱步骤图片文件地址
                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });
    exports('content/recipe/recipe_step_list', {})
});