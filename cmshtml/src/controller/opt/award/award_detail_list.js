layui.define(['table', 'layer', 'form'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,table = layui.table
    ,form = layui.form
    ,layer = layui.layer;
    
    

    layui.data.handler_opt_award_list_table = function (params) {
        //奖品详情列表
        layui.use(['table'], function () {
            var table = layui.table;
            table.render({
                elem: '#LAY-cms-award-detail-list'
                ,url: '/api/awarddetail/list' //获取数据接口
                //,method: "post"
                ,where:{"product_point_id":params.id}
                ,cols: [[
                    {type: 'checkbox', fixed: 'left'}
                    ,{field: 'id', width: 100, title: '排序', sort: true}
                    ,{field: 'image', title: '奖品详情图片', templet:'#award_detail_img_ViewTpl', width: 100, align: 'center'}
                    ,{field: 'createTime', title: '上传时间', minWidth: 150, minHeight:120}
                    ,{field: 'updatetime', title: '更新时间', minWidth: 150, minHeight:120}
                    ,{title: '操作', width: 200, align: 'center', fixed: 'right', toolbar: '#table-award-detail-opt-list'}
                ]]
                ,page: false
                ,limit: 100
                ,limits: [100, 150, 200, 250, 300]
                ,text: '对不起，加载出现异常！'
            });

            //监听工具条
            table.on('tool(LAY-cms-award-detail-list)', function(obj){
                var data = obj.data;
                if(obj.event === 'award_detail_del'){
                    layer.confirm('确定删除此奖品详情？', function(index){
                        award_detail_del({'id':obj.data.id});
                        obj.del();
                        layer.close(index);
                    });
                } else if(obj.event === 'award_detail_edit'){
                    admin.popup({
                        title: '编辑奖品详情'
                        ,area: ['750px', '550px']
                        ,id: 'LAY-popup-opt-award-detail-edit'
                        ,success: function(layero, index){
                            view(this.id).render('app/opt/award/detailedit', data).done(function(){
                                form.render(null, 'cms-award-detail-form');
                            //监听提交
                                form.on('submit(cms-award-detail-form-submit)', function(data){
                                    var field = data.field; //获取提交的字段
                                    // console.log(field)
                                    //提交 Ajax 成功后，关闭当前弹层并重载表格  
                                    //$.ajax({});
                                    award_detail_edit(field)
                                    layer.close(index); //执行关闭 
                                });
                            });
                        }
                    });
                } else if(obj.event === 'detail_checkbig'){
                    // console.log(obj)
                    var imgurl = '';
                    var origin_img = obj.data.image;
                    // origin_img = origin_img.toLocaleLowerCase();
                    if(origin_img.startsWith('http')){
                        imgurl = origin_img;
                    }else{
                        imgurl = layui.setter.basehost + origin_img;
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
    function award_detail_add(data){
        //增加奖品详情
        admin.req({
            type: 'post',
            url: '/api/awarddetail/add', //奖品详情增加
            data:data,
            success: function (result) {
                if (result.success) {
                    form.render();
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-award-detail-list');
            },
            error: function (error) {
            }
        });
    }

    function award_detail_del(data){
        //删除奖品详情
        admin.req({
            type: 'post',
            url: '/api/awarddetail/del', //奖品详情删除
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-award-detail-list');
            },
            error: function (error) {
            }
        });
    }
    
    function award_detail_edit(data){
        //编辑奖品详情
        admin.req({
            type: 'post',
            url: '/api/awarddetail/edit', //奖品详情编辑
            data: data,
            success: function (result) {
                if (result.success) {
                    form.render();
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-award-detail-list');
            },
            error: function (error) {
            }
        });
    }

    var active = {
        detail_batchdel: function(){
          var checkStatus = table.checkStatus('LAY-cms-award-detail-list')
          ,checkData = checkStatus.data; //得到选中的数据
          if(checkData.length === 0){
            return layer.msg('请选择数据');
          }
        
          layer.confirm('确定删除吗？', function(index) {
            $.each(checkData, function (index, item) {
              let data = {};
              data['id'] = item.id;
              award_detail_del(data);
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
        ,detail_add: function(othis){
          admin.popup({
            title: '添加奖品详情'
            ,area: ['750px', '550px']
            ,id: 'LAY-cms-opt-add'
            ,success: function(layero, index){
              view(this.id).render('app/opt/award/detailedit').done(function(){
                form.render(null, 'cms-award-detail-form');
                //监听提交
                // {"id":awardid}
                form.on('submit(cms-award-detail-form-submit)', function(data){
                  var field = data.field; //获取提交的字段
                  field.id = $("#award_for_detail_id").val();
                  console.log(field);
                  //提交 Ajax 成功后，关闭当前弹层并重载表格
                  //$.ajax({});
                  award_detail_add(field);
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

    $(document).on('click', '#uploadfileawarddetail', function(){
        admin.popup({
            title: '上传奖品详情图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-opt-oss-fileupload-award-detail'
            ,success: function(layero, index){
                data = {'operate':2, 'spaceid': document.getElementById('detailuserid').value, 'filename':''};
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
                            document.getElementById('image').value = field.cmsupfiles.slice(0,-1); // 更新奖品详情图片文件地址
                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });
    exports('opt/award/award_detail_list', {})
});