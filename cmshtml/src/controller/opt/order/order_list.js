
layui.define(['table', 'form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,table = layui.table
    ,layer = layui.layer
    ,form = layui.form;

    //订单列表
    table.render({
      elem: '#LAY-cms-order-list'
      ,url: '/api/order/list' //获取数据接口
      ,where: layui.router().search
      ,cols: [[
         {field: 'exchangeorder_id', title: '兑换订单ID', align: 'center'}
        ,{field: 'user_id', title: '用户ID', templet:'#order_user_id', align: 'center' }
        ,{field: 'ume',title: '用户信息', width: 100, align: 'center'}
        ,{field: 'front_image', title: '奖品图片', templet:'#order_img_ViewTpl', align: 'center'}
        ,{field: 'grade_no', title: '奖品价值【积分】', align: 'center' }
        ,{field: 'deliveryAddress', title: '收货地址'}
        ,{field: 'remark', title: '备注信息'}
        ,{field: 'createTime', title: '兑换时间', align: 'center'}
        ,{field: 'express_status', title: '订单状态', templet:'#order_status_Tpl', align: 'center'}
        ,{field: 'logisticsInfo', title: '发货物流信息', align: 'center'}
        ,{title: '操作', minWidth: 450, align: 'center', fixed: 'right', toolbar: '#table-opt-list'}
      ]]
      ,initSort: {
        field: 'id' //排序字段，对应 cols 设定的各字段名
        ,type: 'desc' //排序方式  asc: 升序、desc: 降序、null: 默认排序
      }
      ,page: true
      ,limit: 10
      ,limits: [10, 15, 20, 25, 30]
      ,text: '对不起，加载出现异常！'
    });


    form.render(null, 'cms-order-search-list');
    //监听搜索
    form.on('submit(LAY-cms-order-search)', function(data){
      var field = data.field;
      //console.log("search",field);
      //执行重载
        table.reload('LAY-cms-order-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-order-list)', function(obj){
        var data = obj.data;
        if(obj.event === 'del'){
          layer.confirm('确定删除此订单？', function(index){
              order_set_del({'id':obj.data.id});
              obj.del();
              layer.close(index);
          });
        } else if(obj.event === 'edit'){
          admin.popup({
              title: '编辑订单:' + data.title
              ,area: ['900px', '800px']
              ,id: 'LAY-popup-opt-order-edit'
              ,success: function(layero, index){
                  // data.popindex = index;
                  view(this.id).render('app/opt/order/listform', data).done(function(){
                    submit_order_edit_form(index);
                });
              }
          });
        } else if(obj.event === 'order_step_list'){
          //监听订单步骤按钮
          admin.popup({
            title: '订单步骤:' + data.title
            ,area: ['1150px', '750px']
            ,id: 'LAY-popup-opt-order-step-list-edit'
            ,success: function(layero, index){
                view(this.id).render('app/opt/order/steplist', data)            
            }
          });
        } else if(obj.event === 'checkbig'){
          // console.log(obj)
          var imgurl = '';
          var origin_front_image = obj.data.front_image;
          // origin_front_image = origin_front_image.toLocaleLowerCase();
          if(origin_front_image.startsWith('http')){
            imgurl = origin_front_image;
          }else{
            imgurl = layui.setter.basehost + obj.data.front_image;
          }
          // 查看大图
            layer.open({
            title:'查看大图'
            ,type: 1
            //,skin: 'layui-layer-rim'
            ,shadeClose: true
            ,area: ['auto', 'auto']
            ,opt: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            });
        } else if(obj.event === 'setorderstatus'){
          // 设置订单
          admin.popup({
            title: '设置订单状态:' + data.title
            ,area: ['600px', '550px']
            ,id: 'LAY-popup-opt-order-set-status-edit'
            ,success: function(layero, index){
                view(this.id).render('app/opt/order/setorderstatus', data).done(function(){
                  submit_order_set_statusnum_form(index);
              });
            }
          });
        }
    });

    var active = {
      batchdel:function (othis) {
        // 批量删除订单
        var checkStatus = table.checkStatus('LAY-cms-order-list')
        ,checkData = checkStatus.data; //得到选中的数据
        if(checkData.length === 0){
          return layer.msg('请选择数据');
        }
      
        layer.confirm('确定删除吗？', function(index) {
          $.each(checkData, function (index, item) {
            let data = {};
            data.id = item.id;
            order_set_del(data);
          });
        });
      }
    };
  
    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
      var type = $(this).data('type');
      active[type] ? active[type].call(this) : '';
    });
    function order_set_del(data){
      //设置订单为删除状态
      admin.req({
        type: 'post',
        url: '/api/order/del', //订单步骤增加
        data:data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
          table.reload('LAY-cms-order-list');
        },
        error: function (error) {
        }
      });
    }
  
  function order_edit(data){
      //编辑订单
      admin.req({
          type: 'post',
          url: '/api/order/edit', //订单编辑
          data: data,
          success: function (result) {
              if (result.success) {
                  form.render();
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              table.reload('LAY-cms-order-list');
          },
          error: function (error) {
          }
      });
  }

  function submit_order_edit_form(realindex){
    // 编辑和添加监听
    //监听提交
    form.on('submit(cms-order-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      order_edit(field);
      layer.close(realindex);
    });
  }

  function submit_order_set_statusnum_form(realindex){
    // 设置和编辑状态
    //监听提交
    form.on('submit(cms-order-set-status-edit-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      order_edit(field);
      layer.close(realindex);
    });
    form.on('submit(cms-order-set-num-edit-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      order_edit(field);
      layer.close(realindex);
    });
  }

    // console.log(layui.router().search, layui.router().href);
    exports('opt/order/order_list', {})
});