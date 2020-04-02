layui.define(['index','form', 'dtree'], function(exports){
  var $ = layui.$
  ,admin = layui.admin
  ,view = layui.view
  ,index = layui.index
  ,form= layui.form
  ,dtree = layui.dtree;

  // var DemoTree = null;
  // var DemoTree = dtree.render({
  //   elem: "#demoTree",
  //   url: "/api/class/list",
  //   method: "get",
  //   initLevel: "1",
  //   dataFormat: "list",  //配置data的风格为list
  //   line:true,
  //   toolbar:true,
  //   toolbarStyle: {
  //     title: "分类",
  //     area: ["50%", "400px"]
  //   },
  //   toolbarShow:[], // 默认按钮制空
  //   toolbarExt:[{toolbarId: "Addclassinfo",icon:"dtree-icon-wefill",title:"新增类型",handler: function(node,$div){
  //       layer.msg(JSON.stringify(node));
  //       // 你可以在此添加一个layer.open，里面天上你需要添加的表单元素，就跟你写新增页面是一样的
  //       layer.open({
  //         success: function(layero, index){
  //           form.render();
  //           form.on("submit(addNode_form)",function(data){// 假设form的filter为addNode_form
  //             console.log(data.field);// 从form中取值，数据来源由你自己定
              
  //             var json = {"id":data.field.addId,"title": data.field.addNodeName,"parentId": node.nodeId};
  //             var arr = [{"id":data.field.addId,"title": data.field.addNodeName,"parentId": node.nodeId}];
  //             //DTree5.partialRefreshAdd($div); // 省略第二个参数，则会加载url
  //             //DTree5.partialRefreshAdd($div, json); // 如果是json对象，则会追加元素
  //             //DTree5.partialRefreshAdd($div, arr); //如果是json数组，则会重载节点中的全部子节点
              
  //             layer.close(index);
  //             return false;
  //           });
  //         }
  //       })
  //     }
  //   },
  //   {
  //     toolbarId: "testEdit",icon:"dtree-icon-bianji",title:"类型编辑",handler: function(node,$div){
  //     var res_data = node;
  //     var basicData = node.basicData;  // 取出
  //     basicData = dtree.unescape(basicData); // 转义
  //     var basicDataJSON = JSON.parse(basicData);  // 转成JSON格式 {"sort":999,"iconimg":"","type":1}
  
  //     res_data.sort = basicDataJSON.sort;
  //     res_data.iconimg = basicDataJSON.iconimg;
  //     res_data.type = basicDataJSON.type;

  //     console.log(res_data);
  //     // console.log(basicDataJSON);
  //     layer.open({
  //       type: 1
  //       //,skin: 'layui-layer-rim'
  //       ,shadeClose: false
  //       ,area: ['400px', '500px']
  //       // ,content: eithtmlform
  //       ,content: $("#info").html()
  //       ,success: function(layero, index){
  //         form.render();
  //         form.on("submit(dtree_addNode_form)",function(data){// 假设form的filter为addNode_form
  //           console.log(data.field);// 从form中取值，数据来源由你自己定
            
  //           var json = {"id":data.field.addId,"title": data.field.addNodeName,"parentId": node.nodeId};
  //           var arr = [{"id":data.field.addId,"title": data.field.addNodeName,"parentId": node.nodeId}];
  //           //DTree5.partialRefreshAdd($div); // 省略第二个参数，则会加载url
  //           //DTree5.partialRefreshAdd($div, json); // 如果是json对象，则会追加元素
  //           //DTree5.partialRefreshAdd($div, arr); //如果是json数组，则会重载节点中的全部子节点
            
  //           layer.close(index);
  //           return false;
  //         });
  //       }
  //     });
  //     }
  //   },
  //   {toolbarId: "testDel",icon:"dtree-icon-roundclose",title:"自定义删除",handler: function(node,$div){
  //       layer.msg(JSON.stringify(node));
  //       DTree5.partialRefreshDel($div); // 这样即可删除节点
  //     }
  //   }]
  // });
  
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
      // url: "./json/dtree/demodtree.js", // 获取demo数据
      url: '/api/class/list', //获取数据接口
      formatter: {
        title: function(data) {  // 示例给有子集的节点返回节点统计
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

    res_data.sort = basicDataJSON.sort;
    res_data.iconimg = basicDataJSON.iconimg;
    res_data.type = basicDataJSON.type;
    admin.popup({
      title: '类型编辑'
      ,area: ['450px', '550px']
      ,id: 'LAY-popup-classinfo-edit'
      ,success: function(layero, index){
          // view(this.id).render('app/classinfo/classedit', obj.param)
          view(this.id).render('app/classinfo/classedit', res_data).done(function(){
            // form.render(null, 'cms-classinfo-edit-form');
            //监听编辑
            form.on('submit(cms-classinfo-edit-form-submit)', function(data){
              var field = data.field;
              console.log(field)
              classinfo_edit(field);
              dtreeinit();
              layer.close(index); 
            });
            //监听添加
            // form.render(null, 'cms-classinfo-add-form');
            form.on('submit(cms-classinfo-add-form-submit)', function(data){
              var field = data.field; //添加
              console.log(field)
              classinfo_add(field);
              dtreeinit();
              layer.close(index); //执行关闭 
            });
            //监听删除
            // form.render(null, 'cms-classinfo-delete-form');
            form.on('submit(cms-classinfo-delete-form-submit)', function(data){
              var field = data.field; //编辑
              console.log(field)
              layer.confirm('确定删除?', {
                btn: ['确定','取消'] //按钮
              }, function(){
                classinfo_del(field);
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
          view(this.id).render('app/classinfo/add').done(function(){
            form.render(null, 'cms-classinfo-node-add-form');
            //监听提交
            // {"id":recipeid}
            form.on('submit(cms-classinfo-node-add-form-submit)', function(data){
              var field = data.field; //获取提交的字段
              classinfo_add(field);
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
  
    function classinfo_add(data){
      //增加分类
      admin.req({
          type: 'post',
          url: '/api/class/add', //分类增加
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

  function classinfo_del(data){
      //删除分类
      admin.req({
          type: 'post',
          url: '/api/class/del', //分类删除
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
  
  function classinfo_edit(data){
      //编辑分类
      admin.req({
          type: 'post',
          url: '/api/class/edit', //分类编辑
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

  exports('classinfo/gftree', {})
});
