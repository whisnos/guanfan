
layui.define(['table', 'form', 'layer'], function(exports){
    var $ = layui.$
    ,admin = layui.admin
    ,view = layui.view
    ,table = layui.table
    ,layer = layui.layer
    ,form = layui.form;
  
    layui.use('content/recipe/recipe_step_list', function () {
      // 预加载 食谱推荐 弹窗脚本
      });
    //食谱列表
    table.render({
      elem: '#LAY-cms-recipe-list'
      ,url: '/api/recipe/list' //获取数据接口
      ,where: layui.router().search
      ,cols: [[
        {type: 'checkbox', fixed: 'left'}
        ,{field: 'id', width: 70, title: 'id'}
        ,{field: 'userid', width: 80, title: '用户id', templet:'#recipe_user_id', align: 'center' }
        ,{field: 'title', title: '名称', minWidth: 210}
        ,{field: 'faceimg', title: '封面', templet:'#recipe_img_ViewTpl', width: 100, align: 'center'}
        // ,{field: 'tagKey', title: '标签', width: 150}
        ,{field: 'collectionCount', title: '收藏', width: 80}
        ,{field: 'visitCount', title: '访问', width: 80}
        ,{field: 'isFeatured', title: '精选', templet: '#recipe_featured_Tpl', width: 80, align: 'center'}
        ,{field: 'isEnalbe', title: '启用', templet: '#recipe_isenable_Tpl', width: 80, align: 'center'}
        ,{field: 'status', title: '状态', templet: '#recipe_status_Tpl', minWidth: 80, width: 80, align: 'center'}
        ,{field: 'createtime', title: '上传时间', sort: true,width: 180}
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


    form.render(null, 'cms-recipe-search-list');
    //监听搜索
    form.on('submit(LAY-cms-recipe-search)', function(data){
      var field = data.field;
      //console.log("search",field);
      //执行重载
        table.reload('LAY-cms-recipe-list', {
        where: field,
        page: {
          curr: 1 //重新从第 1 页开始
        }
      });
    });

    //监听工具条
    table.on('tool(LAY-cms-recipe-list)', function(obj){
        var data = obj.data;
        if(obj.event === 'del'){
          layer.confirm('确定删除此食谱？', function(index){
              recipe_set_del({'id':obj.data.id});
              obj.del();
              layer.close(index);
          });
        } else if(obj.event === 'edit'){
          admin.popup({
              title: '编辑食谱:' + data.title
              ,area: ['900px', '800px']
              ,id: 'LAY-popup-content-recipe-edit'
              ,success: function(layero, index){
                  // data.popindex = index;
                  view(this.id).render('app/content/recipe/listform', data).done(function(){
                    submit_recipe_edit_form(index);
                });
              }
          });
        } else if(obj.event === 'recipe_step_list'){
          //监听食谱步骤按钮
          admin.popup({
            title: '食谱步骤:' + data.title
            ,area: ['1150px', '750px']
            ,id: 'LAY-popup-content-recipe-step-list-edit'
            ,success: function(layero, index){
                view(this.id).render('app/content/recipe/steplist', data)            
            }
          });
        } else if(obj.event === 'checkbig'){
          // console.log(obj)
          var imgurl = '';
          var origin_faceimg = obj.data.faceimg;
          // origin_faceimg = origin_faceimg.toLocaleLowerCase();
          if(origin_faceimg.startsWith('http')){
            imgurl = origin_faceimg;
          }else{
            imgurl = layui.setter.basehost + obj.data.faceimg;
          }
          // 查看大图
            layer.open({
            title:'查看大图'
            ,type: 1
            //,skin: 'layui-layer-rim'
            ,shadeClose: true
            ,area: ['auto', 'auto']
            ,content: '<div style="text-align: center; padding: 5px; width: 400px; height:400px"><img src="{imgresource}" style="max-width:100%;max-height:100%"></div>'.replace('{imgresource}', imgurl)
            });
        } else if(obj.event === 'setrecipestatus'){
          // 设置食谱
          admin.popup({
            title: '设置食谱状态:' + data.title
            ,area: ['600px', '550px']
            ,id: 'LAY-popup-content-recipe-set-status-edit'
            ,success: function(layero, index){
                view(this.id).render('app/content/recipe/setrecipestatus', data).done(function(){
                  submit_recipe_set_statusnum_form(index);
              });
            }
          });
        }
    });

    var active = {
      batchdel:function (othis) {
        // 批量删除食谱
        var checkStatus = table.checkStatus('LAY-cms-recipe-list')
        ,checkData = checkStatus.data; //得到选中的数据
        if(checkData.length === 0){
          return layer.msg('请选择数据');
        }
      
        layer.confirm('确定删除吗？', function(index) {
          $.each(checkData, function (index, item) {
            let data = {};
            data.id = item.id;
            recipe_set_del(data);
          });
        });
      }
    };
  
    $('.layui-btn.layuiadmin-btn-list').on('click', function () {
      var type = $(this).data('type');
      active[type] ? active[type].call(this) : '';
    });
    function recipe_set_del(data){
      //设置食谱为删除状态
      admin.req({
        type: 'post',
        url: '/api/recipe/del', //食谱步骤增加
        data:data,
        success: function (result) {
            if (result.success) {
            } else {
                layer.msg(result.msg)
            }
        },
        complete:function (result) {
          table.reload('LAY-cms-recipe-list');
        },
        error: function (error) {
        }
      });
    }
  
  function recipe_edit(data){
      //编辑食谱
      admin.req({
          type: 'post',
          url: '/api/recipe/edit', //食谱编辑
          data: data,
          success: function (result) {
              if (result.success) {
                  form.render();
              } else {
                  layer.msg(result.msg)
              }
          },
          complete:function (result) {
              table.reload('LAY-cms-recipe-list');
          },
          error: function (error) {
          }
      });
  }

  function submit_recipe_edit_form(realindex){
    // 编辑和添加监听
    //监听提交
    form.on('submit(cms-recipe-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      recipe_edit(field);
      layer.close(realindex);
    });
  }

  function submit_recipe_set_statusnum_form(realindex){
    // 设置和编辑状态
    //监听提交
    form.on('submit(cms-recipe-set-status-edit-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      recipe_edit(field);
      layer.close(realindex);
    });
    form.on('submit(cms-recipe-set-num-edit-form-submit)', function(data){
      var field = data.field; //获取提交的字段
      recipe_edit(field);
      layer.close(realindex);
    });
  }

    // console.log(layui.router().search, layui.router().href);
    exports('content/recipe/recipe_list', {})
});