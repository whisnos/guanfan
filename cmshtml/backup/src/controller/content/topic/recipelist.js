layui.define(['table', 'layer', 'form'], function (exports) {
    var $ = layui.$
        , admin = layui.admin
        , view = layui.view
        , table = layui.table
        , layer = layui.layer
        , form = layui.form;

    // 渲染 主题关联食谱列表
    layui.data.handler_topic_list_table = function (params) {
        // console.log(params.id)
        layui.use(['table'], function () {
            // var table = layui.table;
            //关联食谱列表
            table.render({
                elem: '#LAY-cms-topic-recipe-list'
                , url: '/api/topic/recipelist' //获取数据接口
                , page: false //关闭分页
                , where: { 'id': params.id }
                , cols: [[
                    { type: 'checkbox', fixed: 'left' }
                    // , { field: 'id', width: 70, title: 'id', sort: true }
                    // , { field: 'topicid', title: '主题ID', width: 80, minWidth: 80 }
                    , { field: 'recipeid', title: '食谱ID', width: 80, minWidth: 80 }
                    , { field: 'title', title: '标题', minWidth: 100 }
                    , { field: 'isEnable', title: '启用', minWidth: 80, templet: '#topic_recipe_isenable_Tpl', align: 'center'}
                    , { field: 'recipestatus', title: '状态', minWidth: 80, templet: '#topic_recipe_status_Tpl', align: 'center' }
                    , { field: 'reason', title: '推荐理由', minWidth: 150 }
                    , { field: 'sort', title: '排序', sort: true, width: 80, align: 'center' }
                    , { field: 'createtime', title: '上传时间', width: 180 }
                    , { title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#table-topic-recipe-list' }
                ]]
                , text: '对不起，加载出现异常！'
            });
        });
    };

    // form.render(null, 'cms-topic-relation-recipe-edit-form');
    //监听添加,编辑关联食谱
    function form_submit_event(popindex){
        form.on('submit(cms-topic-relation-recipe-edit-form-submit)', function (data) {
            var field = data.field;
            console.log("编辑,添加,关联食谱", field);
            //执行重载
            if (field.relation_id == '') {
                relation_recipe_add(field);
            } else {
                relation_recipe_edit(field);
            }
            layer.close(popindex); //执行关闭
        });
    }

    //监听工具条
    table.on('tool(LAY-cms-topic-recipe-list)', function (obj) {
        var data = obj.data;
        if (obj.event === 'topic_recipe_edit') {
            // 编辑关联食谱
            admin.popup({
                title: '关联食谱编辑'
                , area: ['550px', '350px']
                , id: 'LAY-popup-topic-relation-recipe-form-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/content/topic/recipe_edit', data).done(function(){
                        form_submit_event(index);
                    });
                }
            });
        } else if (obj.event === 'topic_recipe_del') {
            // 是否删除关联食谱
            layer.confirm('确定删除吗?', {
                btn: ['确定', '取消']
            },
                function (index, layero) {
                    // 是否删除主题食谱
                    relation_recipe_del(data);
                    layer.close(layer.index);
                },
                function (index) {
                    layer.close(layer.index);
                }
            );
        }
    });

    var active = {
        topic_recipe_batchdel: function () {
            // 批量删除
            var checkStatus = table.checkStatus('LAY-cms-topic-recipe-list')
                , checkData = checkStatus.data; //得到选中的数据
            if (checkData.length === 0) {
                return layer.msg('请选择数据');
            }

            layer.confirm('确定删除吗？', function (index) {
                $.each(checkData, function (index, item) {
                    relation_recipe_del(item);
                });
                table.reload('LAY-cms-topic-recipe-list');
                layer.msg('已删除');
            });
        }
        , topic_recipe_add: function (othis) {
            // 添加关联食谱
            // 获取当前主题ID
            adddata = { "topicid": $("#hidden_topic_id").val() };
            admin.popup({
                title: '添加关联食谱'
                , area: ['550px', '350px']
                , id: 'LAY-popup-topic-relation-recipe-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/content/topic/recipe_edit', adddata).done(function(){
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

    function relation_recipe_add(data) {
        // 添加关联食谱
        admin.req({
            type: 'post',
            url: '/api/topic/recipeadd', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                    layer.msg('成功')
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-topic-recipe-list');
            },
            error: function (error) {
            }
        });
    }

    function relation_recipe_edit(data) {
        // 修改关联食谱
        admin.req({
            type: 'post',
            url: '/api/topic/recipeedit', //修改
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            }, 
            complete:function (result) {
                table.reload('LAY-cms-topic-recipe-list');
            },
            error: function (error) {
            }
        });
    }
    function relation_recipe_del(data) {
        // 删除关联食谱
        admin.req({
            type: 'post',
            url: '/api/topic/recipedel', //删除
            data: data,
            success: function (result) {
                if (result.success) {
                    table.reload('LAY-cms-topic-recipe-list');
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-topic-recipe-list');
            },
            error: function (error) {
            }
        });
    }
    exports('content/topic/recipelist', {})
});