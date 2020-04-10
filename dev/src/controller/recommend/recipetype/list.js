layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  
    layui.use('recommend/recipetype/recommendrecipelist', function () {
    // 预加载 食谱推荐 弹窗脚本
    });
    //动态列表
    table.render({
      elem: '#LAY-cms-recommend-recipetype-list'
      , url: '/api/recipetype/list' //获取数据接口
      , cols: [[
        // {type: 'checkbox', fixed: 'left'}
        { field: 'id', title: 'ID', minWidth: 80 }
        , { field: 'title', title: '标题', minWidth: 200 }
        , { field: 'sort', title: '排序', minWidth: 100, sort: true }
        , { field: 'status', title: '状态', templet: '#recipetype_status_Tpl', minWidth: 100, align: 'center' }
        , { field: 'updateTime', title: '更新时间', sort: true, minWidth: 180 }
        , { field: 'createTime', title: '上传时间', sort: true, minWidth: 180 }
        , { title: '操作', minWidth: 100, align: 'center', fixed: 'right', toolbar: '#toolbar-recipe-type-content-list' }
      ]]
      , page: true
      , limit: 10
      , limits: [10, 15, 20, 25, 30]
      , text: '对不起，加载出现异常！'
    });
  
    form.render(null, 'cms-recommend-recipetype-search');
    //监听搜索
    form.on('submit(LAY-cms-recommend-recipetype-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-recommend-recipetype-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-recommend-recipetype-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'recipe_type_edit'){
            admin.popup({
                title: '编辑推荐分类'
                , area: ['450px', '350px']
                , id: 'LAY-popup-recommend-recipetype-edit-form'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/recipetype/edit', data).done(function(){
                    submit_recipetype_edit_form(index);
                });
                }
            });
        } else if(obj.event === 'recipe_type_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                recipetype_del({'id':data.id});
            });
        } else if(obj.event === 'recipe_type_relation_caipu') {
            // 食谱推荐
            admin.popup({
                title: '食谱推荐列表'
                , area: ['1150px', '750px']
                , id: 'LAY-popup-recommend-recipe-list-all'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/recipetype/recomrecipelist', data).done(function(){
                });
                }
            });
        }
    });

    var active = {
        recipe_type_add:function (othis) {
            // 添加分类
            admin.popup({
                title: '添加推荐分类'
                , area: ['450px', '350px']
                , id: 'LAY-popup-recommend-recipetype-edit-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/recipetype/edit').done(function(){
                    submit_recipetype_edit_form(index);
                });
                }
            });
        }
      };
    
      $('.layui-btn.layuiadmin-btn-list').on('click', function () {
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
      });

    function submit_recipetype_edit_form(realindex){
        // 编辑和添加监听
        form.on('submit(cms-recommend-recipetype-edit-form-submit)', function (data) {
            var field = data.field;
            console.log(field);
            if(field.id==''){
                //就是添加
                recipetype_add(field);
            }else{
                recipetype_edit(field);
            }
            layer.close(realindex); //执行关闭
        });
    }

    function recipetype_add(data){
        // 添加
        admin.req({
            type: 'post',
            url: '/api/recipetype/add', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipetype-list');
            },
            error: function (error) {
            }
        });
    }

    function recipetype_edit(data){
        // 设置设置状态
        admin.req({
            type: 'post',
            url: '/api/recipetype/edit',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipetype-list');
            },
            error: function (error) {
            }
        });
    }
    function recipetype_del(data){
        // 设置
        admin.req({
            type: 'post',
            url: '/api/recipetype/del', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipetype-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/recipetype/list', {})
});