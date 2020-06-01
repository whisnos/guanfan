layui.define(['index','form', 'dtree'], function(exports){
  var $ = layui.$
  ,admin = layui.admin
  ,view = layui.view
  ,index = layui.index
  ,form= layui.form
  ,dtree = layui.dtree;


  function dtreeinit(){
    DemoTree = dtree.render({
      elem: "#demoTree",
      method: "get",
      initLevel: 1,
      toolbarShow:true,
      drawable:true,
      dataFormat: "list",  //配置data的风格为list
      checkbar:false, //开启复选框
      line:true,
      toolbar:false,
      record:true,
      url: '/api/taoclass/list', //获取数据接口
      formatter: {
        title: function(data) {  // 示例给有子集的节点返回节点统计
          console.log(data);
          var s = data.title;
          if (data.basicData.sort){
            s += ' <span style=\'color:green\'>(' + data.basicData.sort + ')</span>';
          }
          return s;
        }
      }
    });
  }
  dtreeinit();
  // 绑定节点点击
  // dtree.on("node('demoTree')" ,function(obj){
  //   console.log(DemoTree.node);
  //   layer.msg(JSON.stringify(obj.param));
  // });

  dtree.on("nodedblclick('demoTree')" ,function(obj){
    var res_data = obj.param;
    var basicData = obj.param.basicData;  // 取出
    basicData = dtree.unescape(basicData); // 转义
    var basicDataJSON = JSON.parse(basicData);  // 转成JSON格式 {"sort":999,"iconimg":"","type":1}

    // res_data.name = basicData.name;
    // res_data.pid_id = basicDataJSON.pid_id;
    res_data.sort = basicDataJSON.sort;
    res_data.materialId = basicDataJSON.materialId;
    res_data.is_banner = basicDataJSON.is_banner;
    res_data.iconImg = basicDataJSON.iconImg;
    res_data.recommendId = basicDataJSON.recommendId;
    res_data.is_top = basicDataJSON.is_top;
    res_data.level = basicDataJSON.level;
    admin.popup({
      title: '类型编辑'
      ,area: ['450px', '550px']
      ,id: 'LAY-popup-taoclassinfo-edit'
      ,success: function(layero, index){
          // view(this.id).render('app/taoclassinfo/classedit', obj.param)
          view(this.id).render('app/tao/classinfo/classedit', res_data).done(function(){
            form.render(null, 'cms-taoclassinfo-edit-form');
            //监听编辑
            form.on('submit(cms-taoclassinfo-edit-form-submit)', function(data){
              var field = data.field;
              console.log(field);
              taoclassinfo_edit(field);
              dtreeinit();
              layer.close(index);
            });
            //监听添加
            // form.render(null, 'cms-taoclassinfo-add-form');
            form.on('submit(cms-taoclassinfo-add-form-submit)', function(data){
              var field = data.field; //添加
              console.log(field);
              taoclassinfo_add(field);
              dtreeinit();
              layer.close(index); //执行关闭
            });
            //监听删除
            // form.render(null, 'cms-taoclassinfo-delete-form');
            form.on('submit(cms-taoclassinfo-delete-form-submit)', function(data){
              var field = data.field; //编辑
              console.log(field)
              layer.confirm('确定删除?', {
                btn: ['确定','取消'] //按钮
              }, function(){
                taoclassinfo_del(field);
                dtreeinit();
                layer.close(index); //执行关闭
              }, function(){
                // 取消删除
              });
              // dtreeinit();
              // layer.close(index); //执行关闭
            });
          });
        }
    });
  });

  var active = {
    // 添加
    add: function(othis){
      admin.popup({
        title: '添加根节点'
        ,area: ['450px', '400px']
        ,id: 'LAY-cms-content-add'
        ,success: function(layero, index){
          view(this.id).render('app/tao/classinfo/add').done(function(){
            form.render(null, 'cms-taoclassinfo-node-add-form');
            //监听提交
            // {"id":recipeid}
            form.on('submit(cms-taoclassinfo-node-add-form-submit)', function(data){
              var field = data.field; //获取提交的字段
              taoclassinfo_add(field);
              dtreeinit();
              layer.close(index); //执行关闭
            });
          });
        }
      });
    }
  };

  $('.layui-btn.layuiadmin-btn-list').on('click', function(){
      var type = $(this).data('type');
      active[type] ? active[type].call(this) : '';
    });

    function taoclassinfo_add(data){
      //增加分类
      admin.req({
          type: 'post',
          url: '/api/taoclass/add', //分类增加
          data:data,
          success: function (result) {
              if (result.success) {
                  dtreeinit();
                  layer.msg('操作成功', {icon: 1});
              } else {
                  layer.msg(result.msg)
              }
          },
          error: function (error) {
          }
      });
  }

    $(document).on('click', '#adduploadfiletaochannel', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossupload', {'operate':3}).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('iconImg').value = field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                            document.getElementById('iconImg').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });


  function taoclassinfo_del(data){
      //删除分类
      admin.req({
          type: 'post',
          url: '/api/taoclass/del', //分类删除
          data: data,
          success: function (result) {
              if (result.success) {
                  dtreeinit();
                  layer.msg('操作成功', {icon: 1});
              } else {
                  layer.msg(result.msg)
              }
          },
          error: function (error) {
          }
      });
  }

  function taoclassinfo_edit(data){
      //编辑分类
      admin.req({
          type: 'post',
          url: '/api/taoclass/edit', //分类编辑
          data: data,
          success: function (result) {
              if (result.success) {
                  layer.msg('操作成功', {icon: 1});
                  dtreeinit();
                  // form.render();
              } else {
                  layer.msg(result.msg)
              }
          },
          error: function (error) {
          }
      });
  }
    $(document).on('click', '#uploadfiletaochannel', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-taochannel-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2, 'spaceid':document.getElementById('nodeId').value, 'filename':''}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossuploadspace', data).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload-space');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field);
                        if(field.cmsupfiles != ''){
                            document.getElementById('iconImg').value = field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                            document.getElementById('iconImg').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });

    $(document).on('click', '#uploadfiletaosonchannel', function(){
        admin.popup({
            title: '上传图片'
            ,area: ['550px', '450px']
            ,id: 'LAY-popup-content-oss-fileupload'
            ,success: function(layero, index){
                data = {'operate':2}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
                view(this.id).render('app/common/ossupload', {'operate':3}).done(function(){
                    form.render(null, 'layuiadmin-app-oss-fileupload');
                    //文件上传,监听关闭
                    form.on('submit(layuiadmin-app-oss-fileupload)', function(data){
                        var field = data.field; //获取提交的字段
                        console.log(field)
                        if(field.cmsupfiles != ''){
                            document.getElementById('iconSonImg').value = field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                            document.getElementById('iconSonImg').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
                        }
                        layer.close(index); //执行关闭
                    });
                });
            }
        });
    });

    // $(document).on('click', '#uploadfiletaosonchannel', function(){
    //     admin.popup({
    //         title: '上传图片'
    //         ,area: ['550px', '450px']
    //         ,id: 'LAY-popup-taoChannelSon-oss-fileupload'
    //         ,success: function(layero, index){
    //             data = {'operate':2, 'spaceid':document.getElementById('nodeIdSon').value, 'filename':''}; //上传图片类型,1 动态 2 食谱 3 主题 4 海报 5 用户头像 6 高级认证 7 其它
    //             view(this.id).render('app/common/ossuploadspace', data).done(function(){
    //                 form.render(null, 'layuiadmin-app-oss-fileupload-space');
    //                 //文件上传,监听关闭
    //                 form.on('submit(layuiadmin-app-oss-fileupload-space-submit)', function(data){
    //                     var field = data.field; //获取提交的字段
    //                     console.log(field);
    //                     if(field.cmsupfiles != ''){
    //                         document.getElementById('iconImg').value = field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
    //                         document.getElementById('iconImg').src = layui.setter.basehost + field.cmsupfiles.slice(0,-1); // 更新上传图片文件地址
    //                     }
    //                     layer.close(index); //执行关闭
    //                 });
    //             });
    //         }
    //     });
    // });

  exports('/tao/taoclassinfo/gftree', {})
});
