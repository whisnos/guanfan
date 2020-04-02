layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
    

    layui.use('recommend/campaign/contentlist', function () {
        // 预加载 食谱推荐 弹窗脚本
    });
    layui.use('recommend/campaign/joinlist', function () {
        // 预加载 食谱推荐 弹窗脚本
    });
    layui.use('recommend/campaign/pklist', function () {
        // 预加载 食谱推荐 弹窗脚本
    });

    //活动列表
    table.render({
        elem: '#LAY-cms-recommend-campaign-list'
        , url: '/api/campaign/list' //获取数据接口
        , cols: [[
          // {type: 'checkbox', fixed: 'left'}
          { field: 'id', title: 'ID', minWidth: 80 }
          , { field: 'name', title: '活动名称', minWidth: 100 }
          , { field: 'keyname', title: '关键词', minWidth: 100 }
        //   , { field: 'visitcount', title: '访问量', minWidth: 80 }
          , { field: 'ispk', title: '是否PK', templet: '#campaign_pK_Tpl', minWidth: 210, align: 'center' }
          , { field: 'sort', title: '排序', minWidth: 40, sort: true, align: 'center'}
          , { field: 'status', title: '启用', templet: '#campaign_status_Tpl', minWidth: 40, align: 'center' }
          , { field: 'starttime', title: '状态', templet: '#campaign_begining_Tpl', minWidth: 40, align: 'center' }
          , { field: 'starttime', title: '开始时间' }
          , { field: 'endtime', title: '结束时间' }
          , { title: '操作', minWidth: 400, align: 'center', fixed: 'right', toolbar: '#toolbar-campaign-list' }
        ]]
        , page: true
        , limit: 10
        , limits: [10, 15, 20, 25, 30]
        , text: '对不起，加载出现异常！'
    });

    form.render(null, 'cms-recommend-campaign-search');
    //监听搜索
    form.on('submit(LAY-cms-recommend-campaign-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-recommend-campaign-list', {
        where: field,
        page: {
            curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-recommend-campaign-list)', function (obj) {
        var data = obj.data;
        if  (obj.event === 'campaign_edit'){
            admin.popup({
                title: '编辑推荐主题'
                , area: ['850px', '650px']
                , id: 'LAY-popup-recommend-campaign-form-edit'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/edit', data).done(function(){
                        submit_campaign_set_form(index);
                });
                }
            });
        } else if(obj.event === 'campaign_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                compaign_del({'id':data.id});
            });
        } else if(obj.event === 'campaign_set'){
            // 设置活动
            admin.popup({
                title: '设置活动'
                , area: ['450px', '450px']
                , id: 'LAY-popup-recommend-campagin-form-set'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/set', data).done(function(){
                        submit_campaign_set_form(index);
                    });
                }
            });
        } else if(obj.event === 'campaign_content'){
            // 添加修改活动内容
            admin.popup({
                title: '活动详情内容设置'
                , area: ['1080px', '650px']
                , id: 'LAY-popup-recommend-campagin-content-list'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/contentlist', data).done(function(){
                    });
                }
            });
        } else if(obj.event === 'campaign_join_list'){
            // 添加修改活动内容
            admin.popup({
                title: '参与作品列表'
                , area: ['1080px', '650px']
                , id: 'LAY-popup-recommend-campagin-join-list'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/joinlist', data).done(function(){
                    });
                }
            });
        } else if(obj.event === 'campaign_pk_list'){
            // 添加修改活动内容
            admin.popup({
                title: 'PK列表'
                , area: ['800px', '650px']
                , id: 'LAY-popup-recommend-campagin-join-list'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/pklist', data).done(function(){
                    });
                }
            });
        }
        
    });
    
    var active = {
        campaign_add:function (othis) {
            // 添加活动
            admin.popup({
                title: '创建活动'
                , area: ['450px', '230px']
                , id: 'LAY-popup-recommend-campagin-form-add'
                , success: function (layero, index) {
                    view(this.id).render('app/recommend/campaign/add').done(function(){
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



    function submit_campaign_set_form(realindex){
        // 设置表单监听
        form.on('submit(cms-content-campaign-status-set-form-submit)', function (data) {
            var field = data.field;
            compaign_set(field);
            layer.close(realindex); //执行关闭
        });
        // 编辑表单监听
        form.on('submit(cms-recommend-campaign-edit-form-submit)', function (data) {
            var field = data.field;
            compaign_set(field);
            layer.close(realindex); //执行关闭
        });        
    }

    function submit_campaign_add_form(realindex){
        // 添加监听
        form.on('submit(cms-recommend-campaign-add-form-submit)', function (data) {
            var field = data.field;
            compaign_add(field);
            layer.close(realindex); //执行关闭
        });
    }

    function compaign_set(data){
        // 删除活动
        admin.req({
            type: 'post',
            url: '/api/campaign/set',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-list');
            },
            error: function (error) {
            }
        });
    }

    function compaign_del(data){
        // 删除活动
        
        admin.req({
            type: 'post',
            url: '/api/campaign/del',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-list');
            },
            error: function (error) {
            }
        });
    }

    function compaign_add(data){
        // 添加活动
        admin.req({
            type: 'post',
            url: '/api/campaign/add',
            data: data,
            success: function (result) {
                if (result.success) {
                } else {
                    layer.msg(result.msg)
                }
            },
            complete:function (result) {
                table.reload('LAY-cms-recommend-campaign-list');
            },
            error: function (error) {
            }
        });
    }

    exports('recommend/campaign/list', {});
});