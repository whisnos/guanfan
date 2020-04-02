layui.define(['table', 'form', 'layer'], function (exports) {
  var $ = layui.$
    , admin = layui.admin
    , view = layui.view
    , table = layui.table
    , layer = layui.layer
    , form = layui.form;

  layui.use('content/topic/recipelist', function () {
    // 预加载 主题关联弹窗 脚本
  });


  //主题列表
  table.render({
    elem: '#LAY-cms-content-topic-table-list'
    , url: '/api/topic/list' //获取数据接口
    ,where: layui.router().search
    , cols: [[
      {type: 'checkbox', fixed: 'left'}
      , { field: 'id', title: 'id', width: 80, minWidth: 80 }      
      , { field: 'userid', title: '用户ID', width: 80, minWidth: 80, templet: '#topic_user_id', align: 'center'  }
      , { field: 'title', title: '标题', minWidth: 100 }
      , { field: 'faceimg', title: '封面图', templet: '#topic_logo_img_ViewTpl', width: 100, align: 'center' }
      , { field: 'maininfourl', title: '主图', templet: '#topic_main_ViewTpl', width: 100, align: 'center' }
      , { field: 'introduction', title: '简介', minWidth: 150 }
      , { field: 'visitcount', title: '访问量', width: 80, align: 'center' }
      , { field: 'collectioncount', title: '收藏量', width: 80, align: 'center' }
      // , {field: 'isrecommend', title: '加入推荐', templet: '#topic_isrecommend_Tpl', width: 80, align: 'center'}
      , { field: 'isenable', title: '启用',templet:'#topic_isenbale_Tpl', width: 80, align: 'center' }
      , { field: 'status', title: '状态', templet: '#topic_status_Tpl', minWidth: 80, width: 80, align: 'center' }
      , { field: 'updatetime', title: '更新时间', sort: true, minWidth: 180 }
      // , { field: 'createtime', title: '上传时间', sort: true, minWidth: 180 }
      , { title: '操作', minWidth: 260, align: 'center', fixed: 'right', toolbar: '#toolbar-topic-content-list' }
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



  form.render(null, 'cms-content-topic-search');
  //监听搜索
  form.on('submit(LAY-cms-content-topic-search)', function (data) {
    var field = data.field;
    //console.log("search",field);
    //执行重载
    table.reload('LAY-cms-content-topic-table-list', {
      where: field,
      page: {
        curr: 1 //重新从第 1 页开始
      }
    });
  });

  //监听工具条
  table.on('tool(LAY-cms-content-topic-table-list)', function (obj) {
    var data = obj.data;
    if (obj.event === 'topicstatusset') {
      admin.popup({
        title: '主题状态设置'
        , area: ['450px', '450px']
        , id: 'LAY-popup-topic-edit-form'
        , success: function (layero, index) {
          view(this.id).render('app/content/topic/set', data).done(function(){
            submit_topic_statu_set_form(index);
        });
        }
      });
    } else if (obj.event === 'topicedit') {
      admin.popup({
        title: '主题内容编辑'
        , area: ['750px', '1000px']
        , id: 'LAY-popup-topic-edit-form'
        , success: function (layero, index) {
          view(this.id).render('app/content/topic/edit', data).done(function(){
            submit_topic_edit_form(index);
        });
        }
      });
    } else if (obj.event === 'topicrelationrecipe') {
      // 主题关联的食谱
      admin.popup({
        title: '主题关联食谱'
        , area: ['1150px', '750px']
        , id: 'LAY-popup-topic-relation-recipe-list'
        , success: function (layero, index) {
          // layui.data.userverifypopid = index; // 定义全局变量
          view(this.id).render('app/content/topic/recipelist', data);
          // form.render();   //表单渲染，得渲染才会有效果显示出来
        }
      });
    } else if (obj.event === 'check_topic_big') {
      var imgurl = '';
      var origin_faceimg = obj.data.faceimg;
      // origin_faceimg = origin_faceimg.toLocaleLowerCase();
      if (origin_faceimg.startsWith('http')) {
        imgurl = origin_faceimg;
      } else {
        imgurl = layui.setter.basehost + origin_faceimg;
      }
      layer.open({
        title: '查看大图'
        , type: 1
        , shadeClose: true
        , area: ['auto', 'auto']
        , content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
      });
    } else if (obj.event === 'check_topic_main_big') {
      var imgurl = '';
      var origin_faceimg = obj.data.maininfourl;
      // origin_faceimg = origin_faceimg.toLocaleLowerCase();
      if (origin_faceimg.startsWith('http')) {
        imgurl = origin_faceimg;
      } else {
        imgurl = layui.setter.basehost + origin_faceimg;
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
    topic_add: function (othis) {
      // 添加主题
      adddata = { "topicid": $("#id").val() };
      admin.popup({
        title: '添加主题'
        , area: ['750px', '900px']
        , id: 'LAY-popup-topic-edit-form-add'
        , success: function (layero, index) {
          view(this.id).render('app/content/topic/edit', adddata).done(function(){
            submit_topic_edit_form(index);
        });
        }
      });
    },
    topic_batchdel:function (othis) {
      // 删除主题
      var checkStatus = table.checkStatus('LAY-cms-content-topic-table-list')
        , checkData = checkStatus.data; //得到选中的数据
      if (checkData.length === 0) {
          return layer.msg('请选择数据');
      }
      layer.confirm('确定删除吗？', function (index) {
          $.each(checkData, function (index, item) {
            topic_del(item);
          });
          table.reload('LAY-cms-content-topic-table-list');
          layer.msg('已删除');
      });
    }
  };

  $('.layui-btn.layuiadmin-btn-list').on('click', function () {
    var type = $(this).data('type');
    active[type] ? active[type].call(this) : '';
  });

  function submit_topic_statu_set_form(realindex){
    // 主题状态设置监听
    form.on('submit(cms-content-topic-status-set-form-submit)', function (data) {
        var field = data.field;
        topic_set(field);
        layer.close(realindex); //执行关闭
    });
  }

  function submit_topic_edit_form(realindex){
    // 主题编辑和添加监听
    form.on('submit(cms-topic-edit-form-submit)', function (data) {
        var field = data.field;
        if(field.id==''){
          //编辑框没有主题ID,就是添加
          topic_add(field);
        }else{
          topic_edit(field);
        }
        layer.close(realindex); //执行关闭
    });
  }

  function topic_add(data) {
    // 添加主题
    admin.req({
        type: 'post',
        url: '/api/topic/add', //添加
        data: data,
        success: function (result) {
            if (result.success) {
                layer.msg('成功')
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
            table.reload('LAY-cms-content-topic-table-list');
        },
        error: function (error) {
        }
    });
}

function topic_edit(data) {
    // 修改主题
    admin.req({
        type: 'post',
        url: '/api/topic/edit', //修改
        data: data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        }, 
        complete:function (result) {
            table.reload('LAY-cms-content-topic-table-list');
        },
        error: function (error) {
        }
    });
}

function topic_set(data) {
  // 修改主题
  admin.req({
      type: 'post',
      url: '/api/topic/set', //修改
      data: data,
      success: function (result) {
          if (result.success) {
          } else {
              layer.msg(result.msg)
          }
      }, 
      complete:function (result) {
          table.reload('LAY-cms-content-topic-table-list');
      },
      error: function (error) {
      }
  });
}

function topic_del(data) {
    // 删除主题
    admin.req({
        type: 'post',
        url: '/api/topic/del', //删除
        data: data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
            table.reload('LAY-cms-content-topic-table-list');
        },
        error: function (error) {
        }
    });
  }
  
  exports('content/topic/topic_list', {})
});