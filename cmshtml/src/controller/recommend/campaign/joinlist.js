layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
        , admin = layui.admin
        , view = layui.view
        , table = layui.table
        , layer = layui.layer
        , form = layui.form;

    //活动列表
    layui.data.handler_recomend_campaign_join_table = function (params) {
        layui.use(['table'], function () {
            var table = layui.table;
            // console.log(params);
            let name = {};
            if (params.type==2){
                name.joinid = "食谱ID";
                name.img = "食谱封面";
                name.title = "食谱名称";
                name.cnum = "收藏量";
            }else{
                name.joinid = "动态ID";
                name.img = "动态图片";
                name.title = "动态名称";
                name.cnum = "点赞数";
            }
            table.render({
                elem: '#LAY-cms-recommend-campaign-join-list'
                , url: '/api/campaign/join/list' //获取参与列表菜谱接口
                , where: { 'campaignid': params.id, 'jointype': params.type }
                , cols: [[
                    { field: 'id', title: 'ID', minWidth: 80 }
                    , { field: 'userid', title: '用户ID', minWidth: 80 }
                    , { field: 'joinid', title: name.joinid, minWidth: 80, templet: "#campaign_join_type_uri_Tpl", align: 'center'  }
                    , { field: 'img', title: name.img, minWidth: 100, templet: "#campaign_join_img_ViewTpl", align: 'center' }
                    , { field: 'title', title: name.title, minWidth: 100 }
                    , { field: 'cnum', title: name.cnum, minWidth: 100, align: 'center' }
                    , { title: '操作', minWidth: 50, align: 'center', fixed: 'right', toolbar: '#toolbar-campaign-join-list' }
                ]]
                , page: true
                , limit: 10
                , limits: [10, 15, 20, 25, 30]
                , text: '对不起，加载出现异常！'
            });
        });
    };

    form.on('submit(cms-recommend-campaign-join-search-submit)', function (data) {
        var field = data.field;
        //console.log("search",field);
        //执行重载
        table.reload('LAY-cms-recommend-campaign-join-list', {
            where: field,
            page: {
                curr: 1 //重新从第 1 页开始
            }
        });
    });


    //监听工具条
    table.on('tool(LAY-cms-recommend-campaign-join-list)', function (obj) {
        var data = obj.data;
        // console.log(data);
        if (obj.event === 'joinitembig') {
            // console.log(data);
            if (data.jointype == 2){
                // 查看菜谱图片
                if(obj.data.img==null){
                    return;
                }
                var imgurl = '';
                var origin_img = obj.data.img;
                // origin_img = origin_img.toLocaleLowerCase();
                if (origin_img.startsWith('http')) {
                    imgurl = origin_img;
                } else {
                    imgurl = layui.setter.basehost + origin_img;
                }
                // 查看大图
                layer.open({
                    title: '查看大图'
                    , type: 1
                    , skin: 'layui-layer-rim'
                    , shadeClose: true
                    , area: ['auto', 'auto']
                    , content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
                });
            }else{
                // 查看动态图片
                data.momentsimgurl = data.img;
                admin.popup({
                    title: '查看动态图片'
                    , area: ['700px', '600px']
                    , id: 'LAY-popup-campaign-join-dongtai-photo-list'
                    , success: function (layero, index) {
                        view(this.id).render('app/content/dongtai/photo', data).done(function(){
                        });
                    }
                });
            }

        } else if (obj.event === 'campaign_join_del') {
            layer.confirm('确定删除吗？', function (index) {
                compaign_join_del(data);
            });
        }
    });


    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
        var type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
    });

    function compaign_join_del(data) {
        // 删除活动
        admin.req({
            type: 'post',
            url: '/api/campaign/join/del',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete: function (result) {
                table.reload('LAY-cms-recommend-campaign-join-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/campaign/joinlist', {});
});