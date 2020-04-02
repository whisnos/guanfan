layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;
  
    // layui.use('content/dongtai/recipelist', function () {
    //   // 预加载 动态关联弹窗 脚本
    // });
  
  
    //动态列表
    table.render({
      elem: '#LAY-cms-content-dongtai-table-list'
      , url: '/api/dongtai/list' //获取数据接口
      ,where: layui.router().search
      , cols: [[
        {type: 'checkbox', fixed: 'left'}
        , { field: 'id', title: 'ID', minWidth: 80 }
        , { field: 'userid', title: '用户ID', minWidth: 80, templet: '#dongtai_user_id', align: 'center' }
        , { field: 'momentsdescription', title: '动态内容', minWidth: 300}
        , { field: 'momentsimgurl', title: '动态图片', templet: '#dongtai_img_list_ViewTpl', align: 'center' }
        , { field: 'type', title: '类型', templet: '#dongtai_type_Tpl', minWidth: 120,align: 'center' }
        , { field: 'itemid', title: '关联ID', minWidth: 80, templet: '#dongtai_relation_id_Tpl', align: 'center' }
        , { field: 'likecount', title: '点赞数', align: 'center' }
        , { field: 'status', title: '状态', templet: '#dongtai_status_Tpl', minWidth: 100, align: 'center' }
        , { field: 'updatetime', title: '更新时间', sort: true, minWidth: 150 }
        , { field: 'createtime', title: '上传时间', sort: true, minWidth: 150 }
        , { title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#toolbar-dongtai-content-list' }
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

    form.render(null, 'cms-content-dongtai-search');
    //监听搜索
    form.on('submit(LAY-cms-content-dongtai-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-content-dongtai-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-content-dongtai-table-list)', function (obj) {
        var data = obj.data;
        if (obj.event === 'check_dongtai_img') {
            admin.popup({
                title: '查看动态图片'
                , area: ['700px', '600px']
                , id: 'LAY-popup-dongtai-photo-list'
                , success: function (layero, index) {
                    view(this.id).render('app/content/dongtai/photo', data).done(function(){
                    });
                }
            });
        } else if  (obj.event === 'dongtaidel'){
            layer.confirm('确定删除吗？', function (index) {
                dongtai_del(data, index);
            });
        } else if  (obj.event === 'dongtaiset'){
          if (parseInt(data.likecount) <= 8){
            layer.msg('点赞数量不能小于8');
            // layer.close(index);
          }else{
            layer.prompt({title: '修改动态点赞数量', value:data.likecount,sort:'输入点赞数量', formType: 3}, function(pass, index){
              if (parseInt(pass) > 8){
                // console.log(parseInt(pass));
                dongtai_set_likenum({'id':data.id,'likeCount':parseInt(pass)}, index);
              }else{
                layer.msg('点赞数量不能小于8');
              }
              // layer.close(index);
          });
          }

        }
        
    });

    var active = {
        dongtai_batchdel:function (othis) {
          // 删除动态
          var checkStatus = table.checkStatus('LAY-cms-content-dongtai-table-list')
            , checkData = checkStatus.data; //得到选中的数据
          if (checkData.length === 0) {
              return layer.msg('请选择数据');
          }
          layer.confirm('确定删除吗？', function (index) {
              $.each(checkData, function (index, item) {
                dongtai_del(item, index);
              });
          });
        }
      };
    
    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
      var type = $(this).data('type');
      active[type] ? active[type].call(this) : '';
    });
    function dongtai_del(data, index){
      // 添加动态
      admin.req({
          type: 'post',
          url: '/api/dongtai/del', //添加
          data: {'id':data.id},
          success: function (result) {
              if (result.success) {
                  // layer.msg('成功')
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              layer.close(index);
              table.reload('LAY-cms-content-dongtai-table-list');
          },
          error: function (error) {
          }
      });
    };
    function dongtai_set_likenum(data,index){
      // 添加动态
      admin.req({
          type: 'post',
          url: '/api/dongtai/setlike', //添加
          data: data,
          success: function (result) {
              if (result.success) {
                  // layer.msg('成功')
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              layer.close(index);
              table.reload('LAY-cms-content-dongtai-table-list');
          },
          error: function (error) {
          }
      });
    };
    exports('content/dongtai/list', {})
});