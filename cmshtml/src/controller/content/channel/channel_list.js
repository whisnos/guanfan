layui.define(['table', 'form', 'layer'], function (exports) {
    var $ = layui.$
      , admin = layui.admin
      , view = layui.view
      , table = layui.table
      , layer = layui.layer
      , form = layui.form;


    //动态列表
    table.render({
      elem: '#LAY-cms-content-channel-table-list'
      , url: '/api/channel/list' //获取数据接口
      // ,where: layui.router().search
      , cols: [[
        { field: 'id', title: '频道ID',width:150 }
        , { field: 'title', title: '频道名称',width:150, align: 'center' }
        , { field: 'faceImg', title: '频道图片', templet: '#channel_img_list_ViewTpl', minWidth: 150, align: 'center' }
        , { field: 'sort', title: '排序', align: 'center' }
        , { field: 'dynamicCount', title: '动态数量', minWidth: 150,align: 'center'  }
        , { field: 'visitCount', title: '浏览量', minWidth: 150,align: 'center' }
        , { title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#toolbar-channel-type-content-list' }
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

    form.render(null, 'cms-content-channel-search');
    //监听搜索
    form.on('submit(LAY-cms-content-channel-search)', function (data) {
      var field = data.field;
      table.reload('LAY-cms-content-channel-table-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

  //监听工具条
  table.on('tool(LAY-cms-content-channel-table-list)', function (obj) {
    var data = obj.data;
    if (obj.event === 'channel_edit') {
      admin.popup({
        title: '频道内容编辑'
        , area: ['450px', '450px']
        , id: 'LAY-popup-channel-edit-form'
        , success: function (layero, index) {
          view(this.id).render('app/content/channel/edit', data).done(function(){
            submit_channel_edit_form(index);
        });
        }
      });
    } else if(obj.event === 'channel_del'){
            // 删除
            layer.confirm('确定删除吗？', function (index) {
                channel_del({'id':data.id});
            });
        } else if (obj.event === 'check_channel_img') {
      var imgurl = '';
      var origin_faceImg = obj.data.faceImg;
      if (origin_faceImg.startsWith('http')) {
        imgurl = origin_faceImg;
      } else {
        imgurl = layui.setter.basehost + origin_faceImg;
      }
      layer.open({
        title: '查看大图'
        , type: 1
        , shadeClose: true
        , area: ['auto', 'auto']
        , content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
      });
    }
  });


    var active = {
        channel_add: function (othis) {
          // 新增频道
          adddata = { "channelid": $("#id").val() };
          admin.popup({
            title: '新增频道'
            , area: ['450px', '450px']
            , id: 'LAY-popup-channel-edit-form-add'
            , success: function (layero, index) {
              view(this.id).render('app/content/channel/edit', adddata).done(function(){
                submit_channel_edit_form(index);
            });
            }
          });
        },
      };

    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
      var type = $(this).data('type');
      active[type] ? active[type].call(this) : '';
    });


  function submit_channel_edit_form(realindex){
    // 频道编辑和添加监听
    form.on('submit(cms-channel-edit-form-submit)', function (data) {
        var field = data.field;
        if(field.id==''){
          //编辑框没有频道ID,就是添加
          channel_add(field);
        }else{
          channel_edit(field);
        }
        layer.close(realindex); //执行关闭
    });
  }

  function channel_add(data) {
    // 添加频道
    admin.req({
        type: 'post',
        url: '/api/channel/add', //添加
        data: data,
        success: function (result) {
            if (result.success) {
                layer.msg('成功')
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
            table.reload('LAY-cms-content-channel-table-list');
        },
        error: function (error) {
        }
    });
}

  function channel_edit(data) {
    // 修改频道
    admin.req({
        type: 'post',
        url: '/api/channel/edit', //修改
        data: data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
            table.reload('LAY-cms-content-channel-table-list');
        },
        error: function (error) {
        }
    });
}

  function channel_del(data, index){
      // 设置删除动态
      admin.req({
          type: 'post',
          url: '/api/channel/del',
          data: {'id':data.id},
          success: function (result) {
              if (result.success) {
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              layer.close(index);
              table.reload('LAY-cms-content-channel-table-list');
          },
          error: function (error) {
          }
      });
    };

  function channel_set_likenum(data,index){
      // 添加动态
      admin.req({
          type: 'post',
          url: '/api/channel/setlike', //添加
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
              table.reload('LAY-cms-content-channel-table-list');
          },
          error: function (error) {
          }
      });
};
    exports('content/channel/channel_list', {})
});