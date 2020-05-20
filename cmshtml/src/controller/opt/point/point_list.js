layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;


    //动态列表
    table.render({
      elem: '#LAY-cms-opt-point-list'
      , url: '/api/award/list' //获取数据接口
      , cols: [[
        // {type: 'checkbox', fixed: 'left'}
        { field: 'id', title: 'ID', minWidth: 80 }
        , { field: 'point_type', title: '积分类型', minWidth: 80 ,templet: '#opt_point_type_Tpl', align: 'center' }
        , { field: 'grade_no', title: '积分数量', minWidth: 200 }
        , { field: 'status', title: '积分状态', minWidth: 100, sort: true }
        , { field: 'options_type', title: '选项类型', minWidth: 200,width:300, sort: true,templet: '#opt_point_options_type_Tpl', align: 'center'  }
        , { field: 'count', title: '次数', minWidth: 100, sort: true }
        // , { field: 'updatetime', title: '更新时间', sort: true, minWidth: 180 }
        // , { field: 'createTime', title: '上传时间', sort: true, minWidth: 180 }
        , { title: '操作', minWidth: 200, align: 'center', fixed: 'right', toolbar: '#toolbar-point-type-opt-list' }
      ]]
      , page: true
      , limit: 10
      , limits: [10, 15, 20, 25, 30]
      , text: '对不起，加载出现异常！'
    });

    form.render(null, 'cms-opt-point-search');
    //监听搜索
    form.on('submit(LAY-cms-opt-point-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-opt-point-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-opt-point-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'point_type_edit'){
            admin.popup({
                title: '编辑推荐主题'
                , area: ['450px', '450px']
                , id: 'LAY-popup-opt-point-edit-form'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/point/edit', data).done(function(){
                    submit_optpoint_edit_form(index);
                });
                }
            });
        } else if(obj.event === 'point_type_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                point_del({'id':data.id});
            });
        }
    });

    var active = {
        point_type_add:function (othis) {
            // 添加分类
            admin.popup({
                title: '添加推荐主题'
                , area: ['450px', '450px']
                , id: 'LAY-popup-opt-point-edit-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/opt/point/add').done(function(){
                    submit_optpoint_add_form(index);
                });
                }
            });
        }
    };
    function submit_optpoint_add_form(realindex){
        // 添加监听
        form.on('submit(cms-opt-point-add-form-submit)', function (data) {
            var field = data.field;
            point_add(field);
            layer.close(realindex); //执行关闭
        });
    }

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
    var type = $(this).data('type');
    active[type] ? active[type].call(this) : '';
    });

    function submit_optpoint_edit_form(realindex){
        // 编辑和添加监听
        form.on('submit(cms-opt-point-edit-form-submit)', function (data) {
            var field = data.field;
            console.log(field);
                point_edit(field);
            layer.close(realindex); //执行关闭
        });
    }

    function point_add(data){
        // 添加
        admin.req({
            type: 'post',
            url: '/api/point/add', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-point-list');
            },
            error: function (error) {
            }
        });
    }

    function point_edit(data){
        // 设置设置状态
        admin.req({
            type: 'post',
            url: '/api/point/edit',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-point-list');
            },
            error: function (error) {
            }
        });
    }
    function point_del(data){
        // 设置
        admin.req({
            type: 'post',
            url: '/api/point/del', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-opt-point-list');
            },
            error: function (error) {
            }
        });
    }

  exports('opt/point/point_list', {})
});