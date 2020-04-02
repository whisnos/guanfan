layui.define(['table', 'form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,table = layui.table
    ,layer = layui.layer
    ,form = layui.form;
 
    //用户列表
    table.render({
      elem: '#LAY-cms-user-list'
      ,url: '/api/user/list' //获取数据接口
      ,where: layui.router().search
      ,cols: [[
        // {type: 'checkbox', fixed: 'left'}
        {field: 'id', width: 70, title: 'id'}
        ,{field: 'username', title: '昵称', minWidth: 150}
        ,{field: 'headimg', title: '头像', templet:'#user_img_ViewTpl', width: 100, align: 'center'}
        ,{field: 'mobile', title: '手机号', width: 120}
        ,{field: 'sex', title: '性别', templet:'#user_sex_Tpl', width: 80, align: 'center'}
        ,{field: 'birthday', title: '生日', width: 120}
        ,{field: 'tag', title: '标签', width: 100}
        ,{field: 'address', title: '地址', width: 100}
        ,{field: 'personalprofile', title: '个人介绍', width: 100}
        ,{field: 'taste', title: '口味', width: 100}
        ,{field: 'certificationstatus', title: '认证状态', templet: '#user_verify_status_Tpl', width: 100}
        ,{field: 'status', title: '状态', templet: '#user_status_Tpl', minWidth: 80, width: 80, align: 'center'}
        ,{field: 'createtime', title: '上传时间', sort: true,width: 150}
        ,{title: '操作', minWidth: 150, align: 'center', fixed: 'right', toolbar: '#table-content-list'}
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
   
    form.render(null, 'cms-user-search-list');
    //监听搜索
    form.on('submit(LAY-cms-user-search)', function(data){
      var field = data.field;

      // console.log("search",field);
      //执行重载
      table.reload('LAY-cms-user-list', {
          where: field,
          page: {
            curr: 1 //重新从第 1 页开始
          }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-user-list)', function(obj){
        var data = obj.data;
        if(obj.event === 'setstatus'){
          layer.confirm('设置用户状态', {
            btn: ['启用', '禁用', '取消']
          }, function(index, layero){
            // 设置用户启用
            r_d = {};
            r_d.id = data.id;
            r_d.status=0;
            set_user_status(r_d);
            table.reload('LAY-cms-user-list');
            
          }, function(index){
            // 设置用户禁用
            r_d = {};
            r_d.id = data.id;
            r_d.status=-1;
            set_user_status(r_d);
            table.reload('LAY-cms-user-list');

          }, function(index){
            layer.close(layer.index);
          });
        } else if(obj.event === 'checkverify'){
          admin.popup({
              title: '审核用户认证资料'
              ,area: ['650px', '750px']
              ,id: 'LAY-popup-user-verify-form'
              ,success: function(layero, index){
                  // layui.data.userverifypopid = index; // 定义全局变量
                  view(this.id).render('app/user/verifyform', data);
                    form.render();   //表单渲染，得渲染才会有效果显示出来
                }
                  
          });

        } else if(obj.event === 'checkbig'){
          var imgurl = '';
          var origin_faceimg = obj.data.headimg;
          // origin_faceimg = origin_faceimg.toLocaleLowerCase();
          if(origin_faceimg.startsWith('http')){
            imgurl = origin_faceimg;
          }else{
            imgurl = layui.setter.basehost + origin_faceimg;
          }
          // 查看大图
            layer.open({
            title:'查看大图'
            ,type: 1
            //,skin: 'layui-layer-rim'
            ,shadeClose: true
            // ,area: admin.screen() < 2 ? ['80%', '100%'] : ['700px', '500px']
            // ,area: ['480px', '640px']
            ,area: ['auto', 'auto']
            ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            // ,content: '<img src="{imgresource}" class="cms-list-img">'.replace('{imgresource}', layui.setter.basehost + obj.data.bannerimg)
            });
        }
    });

    function set_user_status(data){
      admin.req({
        type: 'post',
        url: '/api/user/del', //设置禁用或启用
        data: data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        error: function (error) {
        }
    });
  }
    exports('user/userlist', {})
});