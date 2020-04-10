layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  
    //活动列表
    layui.data.handler_recomend_campaign_content_table = function(params){
        layui.use(['table'], function () {
            var table = layui.table;
            table.render({
                elem: '#LAY-cms-recommend-campaign-content-list'
                , url: '/api/campaign/content/list' //获取数据接口
                , where: { 'campaignid': params.id, 'type':1 }
                , cols: [[
                  { field: 'id', title: 'ID', minWidth: 80}
                  , { field: 'imgurl', title: '图片地址', minWidth: 100, templet:"#campaign_content_img_ViewTpl", align: 'center' }
                  , { field: 'imgstyle', title: '样式', minWidth: 100 }
                  , { field: 'navtype', title: '类型', templet: '#campaign_content_type_Tpl', minWidth: 100, align: 'center' }
                  , { field: 'navid', title: '跳转ID', minWidth: 100 }
                  , { field: 'createtime', title: '创建时间', minWidth: 180 }
                  , { title: '操作', minWidth: 200, align: 'center', fixed: 'right', toolbar: '#toolbar-campaign-content-list' }
                ]]
                , page: true
                , limit: 10
                , limits: [10, 15, 20, 25, 30]
                , text: '对不起，加载出现异常！'
            });
        });
    };


    //监听工具条
    table.on('tool(LAY-cms-recommend-campaign-content-list)', function (obj) {
        var data = obj.data;
        // console.log(data);
        if(obj.event === 'contentimgbig'){
            console.log(data);
            var imgurl = '';
            var origin_img = obj.data.imgurl;
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
                ,skin: 'layui-layer-rim'
                ,shadeClose: true
                ,area: ['auto', 'auto']
                ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            });
        } else if(obj.event === 'campaign_content_edit'){
            admin.popup({
                title: '编辑活动内容图片'
                , area: ['550px', '650px']
                , id: 'LAY-popup-recommend-campagin-content-form-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/contentedit', data).done(function(){
                        submit_campaign_set_form(index);
                    });
                }
            });
        } else if  (obj.event === 'campaign_content_del'){
            layer.confirm('确定删除吗？', function (index) {
                compaign_content_del(data);
            });
        }
    });
    
    var active = {
        campaign_add:function (othis) {
            // 添加活动内容图片
            let title = "";
            data = {"campaignid":document.getElementById("campaignid").value}
            let selvalue = $("input[name='camcontent']:checked").val();
            if(selvalue == 1){
                title = "添加活动内容图片";
                data.type = 1;
            }else{
                title = "添加开奖内容图片";
                data.type = 2;
            }
            admin.popup({
                title: title
                , area: ['550px', '650px']
                , id: 'LAY-popup-recommend-campagin-content-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/contentadd', data).done(function(){
                        submit_campaign_add_form(index);
                    });
                }
            });
        }
    };

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
    var type = $(this).data('type');
    active[type] ? active[type].call(this) : '';
    });

    form.on('radio(chosecontent)', function(data){
        // 监听 活动内容选择查询事件
        // console.log(data.elem); //得到radio原始DOM对象
        // console.log(data.value); //被点击的radio的value值
        var field = {};
        field.campaignid = document.getElementById("campaignid").value;
        field.type = data.value;
        // console.log(field);
        if (data.value == 1){
            document.getElementById("btnaddcontent").innerHTML = "添加活动图";
        }else{
            document.getElementById("btnaddcontent").innerHTML = "添加开奖图";
        }
        table.reload('LAY-cms-recommend-campaign-content-list', {
            where: field,
            page: {
                curr: 1 //重新从第 1 页开始
            }
        });
    });
    
    function submit_campaign_set_form(realindex){
        // 编辑表单监听
        form.on('submit(cms-recommend-campaign-content-edit-form-submit)', function (data) {
            var field = data.field;
            compaign_content_set(field);
            layer.close(realindex); //执行关闭
        });        
    }

    function submit_campaign_add_form(realindex){
        // 添加监听
        form.on('submit(cms-recommend-campaign-content-add-form-submit)', function (data) {
            var field = data.field;
            compaign_content_add(field);
            layer.close(realindex); //执行关闭
        });
    }

    function compaign_content_set(data){
        // 设置
        admin.req({
            type: 'post',
            url: '/api/campaign/content/edit',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-content-list');
            },
            error: function (error) {
            }
        });
    }

    function compaign_content_del(data){
        // 删除活动
        admin.req({
            type: 'post',
            url: '/api/campaign/content/del',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-content-list');
            },
            error: function (error) {
            }
        });
    }

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
                table.reload('LAY-cms-recommend-campaign-content-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/campaign/contentlist', {});
});