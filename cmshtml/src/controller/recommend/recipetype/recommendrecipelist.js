layui.define(['table', 'layer', 'form'], function (exports) {
    var $ = layui.$
        , admin = layui.admin
        , view = layui.view
        , table = layui.table
        , layer = layui.layer
        , form = layui.form;

    // 渲染 精品分类推荐食谱列表
    layui.data.handler_recomend_recipe_list_table = function (params) {
        // console.log(params);
        layui.use(['table'], function () {
            var table = layui.table;
            //推荐食谱列表
            table.render({
                elem: '#LAY-cms-recommend-recipe-list'
                , url: '/api/recipetype/recipelist' //获取数据接口
                , page: false //关闭分页
                , where: { 'id': params.id }
                , cols: [[
                    { type: 'checkbox', fixed: 'left' }
                    // , { field: 'id', width: 70, title: 'id', sort: true }
                    // , { field: 'recommendid', title: '主题ID', width: 80, minWidth: 80 }
                    , { field: 'id', title: 'ID', width: 80, minWidth: 80 }
                    , { field: 'recipeid', title: '食谱ID', minWidth: 80, templet: "#recommend_recipetype_recipe_id_Tpl", align: 'center'}
                    , { field: 'title', title: '食谱标题', minWidth: 100 }
                    , { field: 'isEnable', title: '启用', minWidth: 100, templet: '#recommend_recipe_isenable_Tpl', align: 'center'}
                    , { field: 'recipestatus', title: '状态', minWidth: 100, templet: '#recommend_recipe_status_Tpl', align: 'center' }
                    , { field: 'sort', title: '排序', width: 100, sort: true, align: 'center' }
                    , { field: 'createtime', title: '上传时间', sort: true, width: 200 }
                    , { title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#table-recommend-recipe-list' }
                ]]
                , text: '对不起，加载出现异常！'
            });
        });
    };

    form.render(null, 'ms-recommend-recipe-edit-form');
    //监听添加,编辑推荐食谱
    function form_submit_event(popindex){
        form.on('submit(cms-recommend-recipe-edit-form-submit)', function (data) {
            var field = data.field;
            console.log("编辑,添加,推荐食谱", field);
            //执行重载
            if (field.id == '') {
                recomend_recipe_add(field);
            } else {
                recomend_recipe_edit(field);
            }
            layer.close(popindex); //执行关闭
        });
    }

    //监听工具条
    table.on('tool(LAY-cms-recommend-recipe-list)', function (obj) {
        var data = obj.data;
        if (obj.event === 'recommend_recipe_edit') {
            // 编辑推荐食谱
            admin.popup({
                title: '推荐食谱编辑'
                , area: ['550px', '350px']
                , id: 'LAY-popup-recommend-relation-recipe-form-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/recipetype/recipe_edit', data).done(function(){
                        form_submit_event(index);
                    });
                }
            });
        } else if (obj.event === 'recommend_recipe_del') {
            // 是否删除推荐食谱
            layer.confirm('确定删除吗?', {
                btn: ['确定', '取消']
            },
                function (index, layero) {
                    // 是否删除主题食谱
                    recomend_recipe_del(data);
                    layer.close(layer.index);
                },
                function (index) {
                    layer.close(layer.index);
                }
            );
        }
    });

    var active = {
        recommend_recipe_batchdel: function () {
            // 批量删除
            var checkStatus = table.checkStatus('LAY-cms-recommend-recipe-list')
                , checkData = checkStatus.data; //得到选中的数据
            if (checkData.length === 0) {
                return layer.msg('请选择数据');
            }

            layer.confirm('确定删除吗？', function (index) {
                $.each(checkData, function (index, item) {
                    recomend_recipe_del(item);
                });
                table.reload('LAY-cms-recommend-recipe-list');
                layer.msg('已删除');
            });
        }
        , recommend_recipe_add: function (othis) {
            // 添加推荐食谱
            // 获取当前主题ID
            adddata = { "categoryid": $("#hidden_recipetype_id").val() };
            admin.popup({
                title: '添加推荐食谱'
                , area: ['550px', '350px']
                , id: 'LAY-popup-recommend-relation-recipe-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/recipetype/recipe_edit', adddata).done(function(){
                        form_submit_event(index);
                    });
                }
            });
        }
    };

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
    });

    function recomend_recipe_add(data) {
        // 添加推荐食谱
        admin.req({
            type: 'post',
            url: '/api/recipetype/recipeadd', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                    layer.msg('成功')
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipe-list');
            },
            error: function (error) {
            }
        });
    }

    function recomend_recipe_edit(data) {
        // 修改推荐食谱
        admin.req({
            type: 'post',
            url: '/api/recipetype/recipeedit', //修改
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            }, 
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipe-list');
            },
            error: function (error) {
            }
        });
    }
    function recomend_recipe_del(data) {
        // 删除推荐食谱
        admin.req({
            type: 'post',
            url: '/api/recipetype/recipedel', //删除
            data: data,
            success: function (result) {
                if (result.success) {
                    table.reload('LAY-cms-recommend-recipe-list');
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-recipe-list');
            },
            error: function (error) {
            }
        });
    }
    exports('recommend/recipetype/recommendrecipelist', {})
});