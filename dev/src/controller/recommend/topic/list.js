layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  

    //动态列表
    table.render({
      elem: '#LAY-cms-recommend-recomtopic-list'
      , url: '/api/recommendtopic/list' //获取数据接口
      , cols: [[
        // {type: 'checkbox', fixed: 'left'}
        { field: 'id', title: 'ID', minWidth: 80 }
        , { field: 'topicId', title: '主题ID', minWidth: 80 ,templet: '#recommend_topic_id_Tpl', align: 'center' }
        , { field: 'title', title: '主题标题', minWidth: 200 }
        , { field: 'recipeNum', title: '食谱数量', minWidth: 100, sort: true }
        , { field: 'reason', title: '理由', minWidth: 200,width:300, sort: true }        
        , { field: 'sort', title: '排序', minWidth: 100, sort: true }
        , { field: 'status', title: '状态', templet: '#recomtopic_status_Tpl', minWidth: 100, align: 'center' }
        , { field: 'updateTime', title: '更新时间', sort: true, minWidth: 180 }
        , { field: 'createTime', title: '上传时间', sort: true, minWidth: 180 }
        , { title: '操作', minWidth: 200, align: 'center', fixed: 'right', toolbar: '#toolbar-recipe-type-content-list' }
      ]]
      , page: true
      , limit: 10
      , limits: [10, 15, 20, 25, 30]
      , text: '对不起，加载出现异常！'
    });
  
    form.render(null, 'cms-recommend-recomtopic-search');
    //监听搜索
    form.on('submit(LAY-cms-recommend-recomtopic-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-recommend-recomtopic-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-recommend-recomtopic-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'recipe_type_edit'){
            admin.popup({
                title: '编辑推荐主题'
                , area: ['450px', '450px']
                , id: 'LAY-popup-recommend-recomtopic-edit-form'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/topic/edit', data).done(function(){
                    submit_recommendtopic_edit_form(index);
                });
                }
            });
        } else if(obj.event === 'recipe_type_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                recomtopic_del({'id':data.id});
            });
        }
    });

    var active = {
        recipe_type_add:function (othis) {
            // 添加分类
            admin.popup({
                title: '添加推荐主题'
                , area: ['450px', '450px']
                , id: 'LAY-popup-recommend-recomtopic-edit-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/topic/edit').done(function(){
                    submit_recommendtopic_edit_form(index);
                });
                }
            });
        }
    };
    
    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
    var type = $(this).data('type');
    active[type] ? active[type].call(this) : '';
    });

    function submit_recommendtopic_edit_form(realindex){
        // 编辑和添加监听
        form.on('submit(cms-recommend-recomtopic-edit-form-submit)', function (data) {
            var field = data.field;
            console.log(field);
            if(field.id==''){
                //就是添加
                recomtopic_add(field);
            }else{
                recomtopic_edit(field);
            }
            layer.close(realindex); //执行关闭
        });
    }

    function recomtopic_add(data){
        // 添加
        admin.req({
            type: 'post',
            url: '/api/recommendtopic/add', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recomtopic-list');
            },
            error: function (error) {
            }
        });
    }

    function recomtopic_edit(data){
        // 设置设置状态
        admin.req({
            type: 'post',
            url: '/api/recommendtopic/edit',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recomtopic-list');
            },
            error: function (error) {
            }
        });
    }
    function recomtopic_del(data){
        // 设置
        admin.req({
            type: 'post',
            url: '/api/recommendtopic/del', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recomtopic-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/topic/list', {})
});