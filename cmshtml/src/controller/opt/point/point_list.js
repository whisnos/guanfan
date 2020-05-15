layui.define(['table', 'form', 'layer', 'router'], function (exports) {
  var $ = layui.$
    , admin = layui.admin
    , view = layui.view
    , table = layui.table
    , layer = layui.layer
    , router = layui.router
    , form = layui.form;


  // 主题列表
  form.render({
    elem: '#LAY-cms-opt-point-table-list'
    , url: '/api/point/list' //获取数据接口
    ,where: layui.router().search
    , cols: [[
      { field: 'id', title: 'id', width: 80, minWidth: 80 }
      , { field: 'point_type', title: '积分类型', width: 80, minWidth: 80, templet: '#point_user_id', align: 'center'  }
      , { field: 'grade_no', title: '积分数', minWidth: 100 }
      , { field: 'count', title: '待定次数', minWidth: 100 }
      , { field: 'options_type', title: '选项类型', minWidth: 100 }
      , { field: 'status', title: '状态', templet: '#point_status_Tpl', minWidth: 80, width: 80, align: 'center' }
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

  form.on('radio(options_type)', function(data){
    // 监听 频道选择查询事件
    var field = {};
    field.status = data.value;
    table.reload('LAY-cms-user-point-table-list', {
        where: field,
        page: {
            curr: 1 //重新从第 1 页开始
        }
    });
});

  // form.render('radio', 'cms-opt-point-search');
    form.render(null, 'cms-opt-point');
  var active = {
    point_batchclose:function (othis) {
      // 删除主题
      var checkStatus = table.checkStatus('LAY-cms-opt-point-table-list')
        , checkData = checkStatus.data; //得到选中的数据
      if (checkData.length === 0) {
          return layer.msg('请选择数据');
      }
      layer.confirm('确定关闭吗？', function (index) {
          $.each(checkData, function (index, item) {
            point_del(item);
          });
          table.reload('LAY-cms-opt-point-table-list');
          layer.msg('已关闭');
      });
    }
  };

  function submit_point_edit_form(realindex){
    // 主题编辑和添加监听
    form.on('submit(cms-point-form-submit)', function (data) {
        var field = data.field;
        if(field.id==''){
          //编辑框没有主题ID,就是添加
          point_add(field);
        }else{
          point_edit(field);
        }
        layer.close(realindex); //执行关闭
    });
  }

  table.on('tool(LAY-app-content-list)', function(obj){
    var data = obj.data;
    if(obj.event === 'edit'){
      admin.popup({
        title: '编辑海报'
        ,area: ['550px', '650px']
        ,id: 'LAY-popup-content-edit'
        ,success: function(layero, index){
          view(this.id).render('app/opt/point/list', data).done(function(){
            form.render(null, 'cms-opt-point');
            //监听提交
            form.on('submit(layuiadmin-app-form-submit)', function(data){
              var field = data.field; //获取提交的字段
              // console.log(field)
              //提交 Ajax 成功后，关闭当前弹层并重载表格
              //$.ajax({});
              point_edit(field, index)

            });

            //监听switch开关
            form.on('switch(status)', function(data){
              // console.log(data)
              // console.log(data.elem); //得到checkbox原始DOM对象
              // console.log(data.elem.checked); //开关是否开启，true或者false
              // console.log(data.value); //开关value值，也可以通过data.elem.value得到
              // console.log(data.othis); //得到美化后的DOM对象
            });
          });
        }
      });
    }
  });




function point_edit(data) {
    // 修改主题
    admin.req({
        type: 'post',
        url: '/api/point/edit', //修改
        data: data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        // complete:function (result) {
        //     table.reload('LAY-cms-opt-point-table-list');
        // },
        error: function (error) {
        }
    });
}

function point_set(data) {
  // 修改主题
  admin.req({
      type: 'post',
      url: '/api/point/set', //修改
      data: data,
      success: function (result) {
          if (result.success) {
          } else {
              layer.msg(result.msg)
          }
      },
      complete:function (result) {
          table.reload('LAY-cms-opt-point-table-list');
      },
      error: function (error) {
      }
  });
}


  exports('opt/point/point_list', {})
});