/**

 @Name：layuiAdmin 内容系统
 @Author：star1029
 @Site：http://www.layui.com/admin/
 @License：LPPL
    
 */


layui.define(['table', 'form'], function(exports){
  var $ = layui.$
  ,admin = layui.admin
  ,view = layui.view
  ,table = layui.table
  ,form = layui.form;


  function banner_del(data){
    //删除海报
    admin.req({
      type: 'post',
      url: '/api/taobanner/del', //海报编辑
      data: data,
      success: function (result) {
          if (result.success) {
              form.render();
          } else {
              layer.msg(result.msg)
          }
      },
      error: function (error) {
      }
    });
  }

  function banner_edit(data,index){
    //编辑海报
    console.log("banner")
    admin.req({
      type: 'post',
      url: '/api/taobanner/edit', //海报编辑
      data:data,
      success: function (result) {
          if (result.success) {
              form.render();
          } else {
              layer.msg(result.msg)
          }
      },
      complete:function (result) {
        layer.close(index); //执行关闭
        layui.table.reload('LAY-app-content-list'); //重载表格
      },

      error: function (error) {
      }
    });
  }
  //海报轮播管理
  table.render({
    elem: '#LAY-app-content-list'
    ,url: '/api/taobanner/list' //模拟接口
    ,cols: [[
      {type: 'checkbox', fixed: 'left'}
      ,{field: 'id', width: 100, title: 'id'}
      ,{field: 'title', title: '海报标题', minWidth: 100}
      ,{field: 'img', title: '海报图片', templet: '#hbimgViewTpl', align: 'center', maxWidth:'100%', maxHeight:'100%'}
      // ,{field: 'recipeid', title: '商品ID', width: 100}
      ,{field: 'content', title: '跳转链接', width: 100}
      // ,{field: 'type', title: '类型', templet: '#banner_type_Tpl', align: 'center'}
      ,{field: 'sort', title: '排序', width: 100, sort: true}
      ,{field: 'backColor', title: '背景色', align: 'center'}
      ,{field: 'createTime', title: '上传时间', sort: true}
      // ,{field: 'status', title: '发布状态', templet: '#buttonTpl', minWidth: 80, width: 100, align: 'center'}
      ,{title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#table-content-list'}
    ]]
    ,page: true
    ,limit: 10
    ,limits: [10, 15, 20, 25, 30]
    ,text: '对不起，加载出现异常！'
  });

  form.on('radio(chosechannel)', function(data){
    // 监听 频道选择查询事件
    var field = {};
    field.channel = data.value;
    table.reload('LAY-app-content-list', {
        where: field,
        page: {
            curr: 1 //重新从第 1 页开始
        }
    });
});

  //监听工具条
  table.on('tool(LAY-app-content-list)', function(obj){
    var data = obj.data;
    if(obj.event === 'del'){
      layer.confirm('确定删除此海报？', function(index){
        banner_del({'id':obj.data.id});
        obj.del();
        layer.close(index);
      });
    } else if(obj.event === 'edit'){
      admin.popup({
        title: '编辑海报'
        ,area: ['550px', '650px']
        ,id: 'LAY-popup-content-edit'
        ,success: function(layero, index){
          view(this.id).render('app/tao/banner/listform', data).done(function(){
            form.render(null, 'layuiadmin-app-form-list');
            //监听提交
            form.on('submit(layuiadmin-app-form-submit)', function(data){
              var field = data.field; //获取提交的字段
              // console.log(field)
              //提交 Ajax 成功后，关闭当前弹层并重载表格
              //$.ajax({});
              banner_edit(field, index)

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
    } else if(obj.event === 'checkbig'){
      // console.log(obj)
      // 查看大图
        layer.open({
          title:'查看大图'
          ,type: 1
          //,skin: 'layui-layer-rim'
          ,shadeClose: true
          // ,area: admin.screen() < 2 ? ['80%', '100%'] : ['700px', '500px']
          // ,area: ['480px', '640px']
          ,area: ['auto', 'auto']
          ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', layui.setter.basehost + obj.data.img)
          // ,content: '<img src="{imgresource}" class="cms-list-img">'.replace('{imgresource}', layui.setter.basehost + obj.data.img)

        });
    }
  });

  $(document).on('click', '#uploadfilebanner', function(){
      admin.popup({
          title: '上传图片'
          ,area: ['550px', '450px']
          ,id: 'LAY-popup-content-oss-fileupload'
          ,success: function(layero, index){
              data = {'operate':2}; //上传图片类型,1 动态 2 商品 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
              view(this.id).render('app/common/ossupload', {'operate':2}).done(function(){
                  form.render(null, 'layuiadmin-app-oss-fileupload');
                  //文件上传,监听关闭
                  form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                      var field = data.field; //获取提交的字段
                      // console.log(field)
                      if(field.cmsupfiles != ''){
                          document.getElementById('img').value = field.cmsupfiles.slice(0,-1); // 更新商品图片文件地址
                      }
                      layer.close(index); //执行关闭 
                  });
              });
          }
      });
  });
  exports('/tao/banner/list', {})
});