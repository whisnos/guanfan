(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0b37a0"],{2914:function(t,e,i){"use strict";i.r(e);var s=function(){var t=this,e=t.$createElement,i=t._self._c||e;return i("div",[i("van-nav-bar",{staticClass:"hader",attrs:{title:"今日主题","left-text":"返回","left-arrow":""},on:{"click-left":function(e){return t.back()}}},[1!=t.isiOS&&1!=t.isWeixin?i("a",{attrs:{slot:"right",href:"https://m.guanfan.top/#/app"},slot:"right"},[i("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?i("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[i("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isWeixin?i("a",{attrs:{slot:"right",href:"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU0NTg5ODQzNA==&scene=124#wechat_redirect"},slot:"right"},[i("van-button",{attrs:{type:"primary",size:"small"}},[t._v("关注")])],1):t._e()]),i("LoadMore",{attrs:{onLoadMore:t.onLoadMore,enableLoadMore:t.enableLoadMore}},[i("div",{staticClass:"cont mt10 clearfix"},[i("div",{staticClass:"food-list1"},[i("ul",t._l(t.themeList,function(e,s){return i("li",{key:s,on:{click:function(i){return t.bookDetail(e.topicid)}}},[i("div",{staticClass:"foodlist-img",style:{backgroundImage:"url("+t.osshost+e.topicimg+t.listpic+")"}}),i("div",{staticClass:"food-list1-tit text-cut"},[t._v(t._s(e.title))]),i("div",{staticClass:"user"},[i("img",{attrs:{src:t.osshost+e.faceimg+t.userface}}),i("span",[t._v(t._s(e.nickname))]),i("i",{staticClass:"icon-like2 van-icon van-icon-like"},[t._v(t._s(e.collections))])])])}),0)])])]),i("Totop")],1)},a=[],o=(i("4917"),i("4328")),n=i.n(o),r=i("bc3a"),c=i.n(r),l=i("eafa"),p=i("83e6"),u={name:"cookbookinfo",components:{LoadMore:l["a"],Totop:p["a"]},data:function(){return{num:13,enableLoadMore:!0,page:1,themeList:[],osshost:"https://guanfan.oss-cn-hangzhou.aliyuncs.com/",listpic:"?x-oss-process=style/list-img",userface:"?x-oss-process=style/user-img",detailpic:"?x-oss-process=style/detail-img",isWeixin:"",isiOS:""}},created:function(){this.getTheme(),this.getwx(),this.appSource()},methods:{getwx:function(){var t=window.navigator.userAgent.toLowerCase();"micromessenger"==t.match(/MicroMessenger/i)?this.isWeixin=!0:this.isWeixin=!1},appSource:function(){var t=navigator.userAgent;navigator.appVersion;t.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)?this.isiOS=!0:this.isiOS=!1},onLoadMore:function(t){var e=this;setTimeout(function(){e.enableLoadMore&&(e.page=e.page+1,e.getThemeList(),t())},500)},getTheme:function(){var t=this,e=n.a.stringify({topictype:1,page:this.page});c()({method:"post",url:"/subject/topiclist",headers:{"Content-Type":"application/x-www-form-urlencoded"},data:e}).then(function(e){e.data.result.length<10&&(t.enableLoadMore=!1),t.themeList=t.themeList.concat(e.data.result)})},bookDetail:function(t){this.$router.push({path:"/themeinfo",query:{id:t}})},back:function(){this.$router.go(-1)}}},h=u,m=i("2877"),d=Object(m["a"])(h,s,a,!1,null,null,null);e["default"]=d.exports}}]);
//# sourceMappingURL=chunk-2d0b37a0.96b501b9.js.map