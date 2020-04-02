layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  
    //活动列表
    layui.data.handler_recomend_campaign_pklist_table = function(params){
        layui.use(['table'], function () {
            var table = layui.table;
            table.render({
                elem: '#LAY-cms-recommend-campaign-pklist'
                , url: '/api/campaign/pk/list' //获pk取数据接口
                , where: { 'campaignid': params.id, 'jointype':4, 'joinid':1 }
                , cols: [[
                  { field: 'id', title: 'ID', minWidth: 80}
                  , { field: 'userid', title: '用户ID', minWidth: 100, templet:"#recommend_campaign_user_id_Tpl", align: 'center' }
                //   , { field: 'joinid', title: 'PK值', templet: '#campaign_pklist_type_Tpl', minWidth: 100, align: 'center' }
                  , { field: 'createtime', title: '创建时间', minWidth: 180 }
                //   , { title: '操作', minWidth: 200, align: 'center', fixed: 'right', toolbar: '#toolbar-campaign-pk-list' }
                ]]
                , page: true
                , limit: 10
                , limits: [10, 15, 20, 25, 30]
                , text: '对不起，加载出现异常！'
            });
        });
    };

    //监听工具条
    table.on('tool(LAY-cms-recommend-campaign-pk-list)', function (obj) {
        var data = obj.data;
        // console.log(data);
        if (obj.event === 'campaign_content_del'){
            layer.confirm('确定删除吗？', function (index) {
                compaign_pk_del(data);
            });
        }
    });

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
    });

    form.on('radio(chosepkvalue)', function(data){
        // 监听 查询选择PK投票数量
        var field = {};
        field.campaignid = document.getElementById("campaignid").value;
        field.joinid = data.value;
        // console.log(data.value);
        table.reload('LAY-cms-recommend-campaign-pklist', {
            where: field,
            page: {
                curr: 1 //重新从第 1 页开始
            }
        });
    });

    function compaign_content_add(data){
        // 添加活动
        admin.req({
            type: 'post',
            url: '/api/campaign/content/add',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-pk-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/campaign/pklist', {});
});