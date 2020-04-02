layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  
  
    //动态列表
    table.render({
      elem: '#LAY-cms-content-report-table-list'
      , url: '/api/report/list' //获取数据接口
      , cols: [[
        {type: 'checkbox', fixed: 'left'}
        , { field: 'id', title: 'id', minWidth: 80 }
        , { field: 'userid', title: '用户ID', minWidth: 80, templet: '#report_user_id', align: 'center' }
        , { field: 'type', title: '内容类型', templet: '#report_content_type_Tpl', minWidth: 80 }
        , { field: 'itemid', title: '内容ID',  minWidth: 80, templet: '#report_content_id_Tpl',  align: 'center' }
        , { field: 'reportreason', title: '举报原因', minWidth: 100 }
        , { field: 'reportdescription', title: '举报描述', minWidth: 300}
        , { field: 'status', title: '状态', templet: '#report_status_Tpl', minWidth: 80, align: 'center' }
        , { field: 'updatetime', title: '更新时间', sort: true, minWidth: 160 }
        , { field: 'createtime', title: '上传时间', sort: true, minWidth: 160 }
        , { title: '操作', minWidth: 100, align: 'center', fixed: 'right', toolbar: '#toolbar-report-content-list' }
      ]]
      ,initSort: {
        field: 'id' //排序字段，对应 cols 设定的各字段名
        ,type: 'desc' //排序方式  asc: 升序、desc: 降序、null: 默认排序
      }
      , page: true
      , limit: 10
      , limits: [10, 15, 20, 25, 30]
      , text: '对不起，加载出现异常！'
    });
  
    form.render(null, 'cms-content-report-search');
    //监听搜索
    form.on('submit(LAY-cms-content-report-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-content-report-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-content-report-table-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'report_set'){
            layer.confirm('设定举报状态', {
                btn: ['举报消除', '举报成功', '取消']
            },
                function (index, layero) {
                    // 消除
                    report_set({'id':data.id, 'status':1});
                    layer.close(layer.index);
                },
                function (index, layero) {
                    // 成功
                    report_set({'id':data.id, 'status':2});
                    layer.close(layer.index);
                },
                function (index) {
                    layer.close(layer.index);
                }
            );
        }
    });

    var active = {
        report_batch_set:function (othis) {
          // 设置举报状态
            var checkStatus = table.checkStatus('LAY-cms-content-report-table-list')
                , checkData = checkStatus.data; //得到选中的数据
            if (checkData.length === 0) {
                return layer.msg('请选择数据');
            }
            layer.confirm('设定举报状态', {
                btn: ['举报消除', '举报成功', '取消']
            },
                function (index, layero) {
                    // 消除
                    $.each(checkData, function (index, item) {
                        report_set({'id':item.id, 'status':1});
                    });
                },
                function (index, layero) {
                    // 成功
                    $.each(checkData, function (index, item) {
                        report_set({'id':item.id, 'status':2});
                    });
                },
                function (index) {
                    layer.close(layer.index);
                }
            );
        }
      };
    
      $('.layui-btn.layuiadmin-btn-list').on('click', function () {
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
      });

    function report_set(data){
        // 设置举报状态
        admin.req({
            type: 'post',
            url: '/api/report/set', //添加
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-content-report-table-list');
            },
            error: function (error) {
            }
        });
    }
    exports('content/report/list', {})
});