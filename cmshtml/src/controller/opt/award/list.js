layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;

    layui.use('opt/award/award_detail_list', function (params) {
      // 预加载 积分奖品详情 弹窗脚本
      });
    //积分奖品列表
    table.render({
        elem: '#LAY-cms-opt-award-list'
        , url: '/api/award/list' //获取数据接口
        , cols: [[
          { field: 'id', title: '奖品ID', width: 80, align: 'center'  }
          , { field: 'title', title: '奖品名称', width: 250 }
          , { field: 'front_image', title: '奖品图片', minWidth: 100, templet:'#award_img_ViewTpl', width: 100, align: 'center' }
          , { field: 'grade_no', title: '奖品价值【积分】', width: 150, align: 'center' }
          , { field: 'sku_no', title: '奖品库存(剩余)', width: 150, align: 'center' }
          , { field: 'status', title: '启用', templet: '#award_status_Tpl', width: 80, align: 'center' }
          , { title: '奖品详情', width: 150, templet:'#award_img_Detail_ViewTpl', align: 'center' }
          , { field: 'sort', title: '排序', width: 80, sort: true, align: 'center'}
          , { title: '操作', minWidth: 200, align: 'center', fixed: 'right', toolbar: '#toolbar-award-list' }
        ]]
        , page: true
        , limit: 10
        , limits: [10, 15, 20, 25, 30]
        , text: '对不起，加载出现异常！'
    });

    form.render(null, 'LAY-cms-opt-award-list');
    //监听搜索
    form.on('submit(LAY-cms-opt-award-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-opt-award-list', {
        where: field,
        page: {
            curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-opt-award-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'award_edit'){
            admin.popup({
                title: '编辑积分奖品'
                , area: ['600px', '500px']
                , id: 'LAY-popup-opt-award-form-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/edit', data).done(function(){
                        submit_award_edit_form(index);
                });
                }
            });
        } else if (obj.event === 'award_detail_edit'){
            admin.popup({
                title: '编辑积分奖品详情: ' + data.title
                , area: ['1150px', '750px']
                , id: 'LAY-popup-opt-award-detail-status-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/detaillist', data)
                }
            });
        } else if(obj.event === 'checkbig'){
          // console.log(obj)
          var imgurl = '';
          var origin_front_image = obj.data.front_image;
          // origin_front_image = origin_front_image.toLocaleLowerCase();
          if(origin_front_image.startsWith('http')){
            imgurl = origin_front_image;
          }else{
            imgurl = layui.setter.basehost + obj.data.front_image;
          }
          // 查看大图
            layer.open({
            title:'查看大图'
            ,type: 1
            //,skin: 'layui-layer-rim'
            ,shadeClose: true
            ,area: ['auto', 'auto']
            ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            });
        } else if(obj.event === 'checkbigdetail'){
          console.log(obj, 444444444444);
          var imgurl = '';
          var origin_front_image = obj.data.front_image;
          // origin_front_image = origin_front_image.toLocaleLowerCase();
          if(origin_front_image.startsWith('http')){
            imgurl = origin_front_image;
              console.log(obj, 55555555555555555);
          }else{
            imgurl = layui.setter.basehost + obj.data.front_image;
            console.log(obj, 666666666666666666666);
          }
          // 查看大图
            layer.open({
            title:'查看大图'
            ,type: 1
            //,skin: 'layui-layer-rim'
            ,shadeClose: true
            ,area: ['auto', 'auto']
            ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            });
        }
        else if(obj.event === 'award_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                award_del({'id':data.id});
            });
        } else if(obj.event === 'award_set'){
            // 下架积分奖品
            admin.popup({
                title: '设置积分奖品状态' + data.title
                , area: ['450px', '450px']
                , id: 'LAY-popup-opt-award-form-set'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/set', data).done(function(){
                        submit_award_set_form(index);
                    });
                }
            });
        } else if(obj.event === 'award_opt'){
            // 添加修改积分奖品内容
            admin.popup({
                title: '积分奖品详情内容设置'
                , area: ['1080px', '650px']
                , id: 'LAY-popup-opt-award-opt-list'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/optlist', data).done(function(){
                    });
                }
            });
        } else if(obj.event === 'award_join_list'){
            // 添加修改积分奖品内容
            admin.popup({
                title: '参与作品列表'
                , area: ['1080px', '650px']
                , id: 'LAY-popup-opt-award-join-list'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/joinlist', data).done(function(){
                    });
                }
            });
        } else if(obj.event === 'award_pk_list'){
            // 添加修改积分奖品内容
            admin.popup({
                title: 'PK列表'
                , area: ['800px', '650px']
                , id: 'LAY-popup-opt-award-join-list'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/pklist', data).done(function(){
                    });
                }
            });
        }
        
    });
    
    var active = {
        award_add:function (othis) {
            // 添加积分奖品
            admin.popup({
                title: '创建积分奖品'
                , area: ['450px', '230px']
                , id: 'LAY-popup-opt-award-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/award/add').done(function(){
                        submit_award_add_form(index);
                    });
                }
            });
        }
    };

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
    var type = $(this).data('type');
    active[type] ? active[type].call(this) : '';
    });

    
  function award_edit(data){
      //编辑食谱
      admin.req({
          type: 'post',
          url: '/api/award/edit', //食谱编辑
          data: data,
          success: function (result) {
              if (result.success) {
                  form.render();
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              table.reload('LAY-cms-opt-award-list');
          },
          error: function (error) {
          }
      });
  }


  function submit_award_edit_form(realindex){
    // 编辑和添加监听
    //监听提交
    form.on('submit(cms-award-edit-submit)', function(data){
      var field = data.field; //获取提交的字段
      award_edit(field);
      layer.close(realindex);
    });
  }
    

    function submit_award_set_form(realindex){
        // 设置表单监听
        form.on('submit(cms-opt-award-status-set-form-submit)', function (data) {
            var field = data.field;
            award_set(field);
            layer.close(realindex); //执行关闭
        });
        // 编辑表单监听
        form.on('submit(cms-opt-award-edit-form-submit)', function (data) {
            var field = data.field;
            award_set(field);
            layer.close(realindex); //执行关闭
        });        
    }

    function submit_award_add_form(realindex){
        // 添加监听
        form.on('submit(cms-opt-award-add-form-submit)', function (data) {
            var field = data.field;
            award_add(field);
            layer.close(realindex); //执行关闭
        });
    }

    function award_set(data){
        // 编辑积分奖品
        admin.req({
            type: 'post',
            url: '/api/award/set',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-award-list');
            },
            error: function (error) {
            }
        });
    }

    function award_del(data){
        // 删除积分奖品
        
        admin.req({
            type: 'post',
            url: '/api/award/del',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-award-list');
            },
            error: function (error) {
            }
        });
    }

    function award_add(data){
        // 添加积分奖品
        admin.req({
            type: 'post',
            url: '/api/award/add',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-award-list');
            },
            error: function (error) {
            }
        });
    }

    exports('opt/award/list', {});
});