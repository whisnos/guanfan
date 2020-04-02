webpackJsonp([7],{K5Z0:function(t,e,o){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var s=o("JJSs"),i=o("wqlu"),n=o("mzkE"),a=o("3/Li"),c=o("qi15"),r=o("zL8q"),l=o("GKmE"),d=o("/Z0X"),u={components:{headerNav:s.a,FoodItem:i.a,FooterBottom:n.a},data:function(){return{osshost:"https://guanfan.oss-cn-hangzhou.aliyuncs.com/",topicid:"",type:"",form:{title:"",topicimg:null,introduction:"",relationrecipe:""},foodList:[{id:0,recipeid:"",sort:100,reason:""}]}},created:function(){this.topicid=this.$route.query.id,this.type=this.$route.query.type,3==this.type&&this.getDataInfo(this.topicid)},mounted:function(){},methods:{delthemeFood:function(t){var e=this;if(-1!==t)if(0!==this.foodList[t].id){var o=this.foodList[t].id;Object(c.b)(this.topicid,o).then(function(o){o.data.success?(Object(r.Message)({message:"关联食谱已删除",type:"success",duration:5e3}),e.foodList.splice(t,1)):Object(r.Message)({message:o.message,type:"error",duration:5e3})}).catch(function(t){e.$router.push({path:"/login"})})}else this.foodList.splice(t,1)},addthemeFood:function(){var t=this.foodList.length,e={id:0,recipeid:"",sort:this.foodList[t-1].sort-1,reason:""};this.foodList.push(e)},onSubmit:function(){for(var t=this,e="",o=0;o<this.foodList.length;o++)e+=0==o?this.foodList[o].id+"#"+this.foodList[o].sort+"#"+this.foodList[o].recipeid+"#"+this.foodList[o].reason:"|"+this.foodList[o].id+"#"+this.foodList[o].sort+"#"+this.foodList[o].recipeid+"#"+this.foodList[o].reason;this.form.relationrecipe=e,3==this.type?(this.form.topicid=this.topicid,Object(c.h)(this.form).then(function(e){e.data.success&&(Object(r.Message)({message:"修改成功！",type:"success",duration:5e3}),t.$router.go(-1))}).then(function(t){console.log(t)})):Object(c.i)(this.form).then(function(e){e.data.success&&(Object(r.Message)({message:"发布成功！",type:"success",duration:5e3}),t.$router.go(-1))}).then(function(t){console.log(t)})},handleRemove:function(){this.form.topicimg=null},handleHttpRequest:function(t){var e=this,o=t.file.name;Object(a.i)(5).then(function(s){var i=s.data.result,n=void 0;n=i.spaceid+"/"+l.a.imgMd5(o,n,"topic"),new d({region:"oss-cn-hangzhou",accessKeyId:i.AccessKeyId,accessKeySecret:i.AccessKeySecret,stsToken:i.SecurityToken,bucket:"guanfan"}).put(n,t.file).then(function(t){e.form.topicimg=t.name,console.log("头像上传成功")}).catch(function(t){console.log(t)})}).catch(function(t){console.log(t)})},getDataInfo:function(t){var e=this;Object(c.c)(t).then(function(t){var o=t.data;o.success?(e.form=o.result,e.foodList=e.form.cplist):Object(r.Message)({message:t.message,type:"error",duration:5e3})}).catch(function(t){console.log(t)})}}},f={render:function(){var t=this,e=t.$createElement,o=t._self._c||e;return o("div",[o("div",{staticClass:"content",attrs:{id:"header"}},[o("header-nav")],1),t._v(" "),o("div",{staticClass:"content padding-top-100"},[o("el-form",{ref:"form",attrs:{model:t.form,"label-width":"80px"}},[o("el-form-item",{attrs:{label:"封面图"}},[o("el-upload",{staticClass:"avatar-uploader",attrs:{action:"#","http-request":t.handleHttpRequest,"show-file-list":!1,"on-remove":t.handleRemove}},[null!=t.form.topicimg?o("img",{staticClass:"avatar",attrs:{src:t.osshost+t.form.topicimg}}):o("i",{staticClass:"el-icon-plus step-upicon"},[t._v("点击上传")])]),t._v(" "),o("div",{staticClass:"el-upload__tip",attrs:{slot:"tip"},slot:"tip"},[t._v("只能上传jpg/png文件，且不超过500kb")]),t._v(" "),o("el-tag",{attrs:{type:"info"}},[t._v("只能上传jpg/png文件，且不超过5mb")])],1),t._v(" "),o("el-form-item",{attrs:{label:"主题名称"}},[o("el-input",{model:{value:t.form.title,callback:function(e){t.$set(t.form,"title",e)},expression:"form.title"}})],1),t._v(" "),o("el-form-item",{attrs:{label:"主题简介"}},[o("el-input",{attrs:{type:"textarea"},model:{value:t.form.introduction,callback:function(e){t.$set(t.form,"introduction",e)},expression:"form.introduction"}})],1),t._v(" "),o("el-form-item",{attrs:{label:"推荐食谱"}},[o("el-tag",{attrs:{type:"info"}},[t._v("(填入管饭网的菜谱ID来添加菜谱，通过菜谱链接查看ID，如https://www.guanfan.top/cookbook?id=43639填入43639即可)")]),t._v(" "),t._l(t.foodList,function(e,s){return o("el-form-item",{key:s,staticClass:"mt20",attrs:{label:"食谱"+parseInt(s+1)}},[o("el-col",{attrs:{span:12}},[o("el-input",{model:{value:e.recipeid,callback:function(o){t.$set(e,"recipeid",o)},expression:"domain.recipeid"}}),t._v(" "),o("el-input",{attrs:{type:"textarea"},model:{value:e.reason,callback:function(o){t.$set(e,"reason",o)},expression:"domain.reason"}})],1),t._v(" "),o("el-col",{staticClass:"ml10",attrs:{span:2}},[o("el-button",{attrs:{type:"danger",icon:"el-icon-delete",circle:"",plain:""},on:{click:function(e){return e.preventDefault(),t.delthemeFood(s)}}})],1)],1)}),t._v(" "),o("el-form-item",{staticClass:"mt20"},[o("el-button",{on:{click:function(e){return t.addthemeFood()}}},[t._v("添加1个食谱")])],1)],2),t._v(" "),o("el-form-item",[o("el-button",{attrs:{type:"success"},on:{click:t.onSubmit}},[t._v("发布主题")])],1)],1)],1),t._v(" "),o("FooterBottom")],1)},staticRenderFns:[]};var p=o("VU/8")(u,f,!1,function(t){o("pa4a")},"data-v-a7a008de",null);e.default=p.exports},pa4a:function(t,e){}});
//# sourceMappingURL=7.5ba2bf37a7e429cc6bca.js.map