(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-25f39a2d"],{"28a5":function(t,i,e){"use strict";var s=e("aae3"),a=e("cb7c"),n=e("ebd6"),l=e("0390"),r=e("9def"),o=e("5f1b"),c=e("520a"),u=e("79e5"),d=Math.min,m=[].push,f="split",p="length",h="lastIndex",g=4294967295,v=!u(function(){RegExp(g,"y")});e("214f")("split",2,function(t,i,e,u){var x;return x="c"=="abbc"[f](/(b)*/)[1]||4!="test"[f](/(?:)/,-1)[p]||2!="ab"[f](/(?:ab)*/)[p]||4!="."[f](/(.?)(.?)/)[p]||"."[f](/()()/)[p]>1||""[f](/.?/)[p]?function(t,i){var a=String(this);if(void 0===t&&0===i)return[];if(!s(t))return e.call(a,t,i);var n,l,r,o=[],u=(t.ignoreCase?"i":"")+(t.multiline?"m":"")+(t.unicode?"u":"")+(t.sticky?"y":""),d=0,f=void 0===i?g:i>>>0,v=new RegExp(t.source,u+"g");while(n=c.call(v,a)){if(l=v[h],l>d&&(o.push(a.slice(d,n.index)),n[p]>1&&n.index<a[p]&&m.apply(o,n.slice(1)),r=n[0][p],d=l,o[p]>=f))break;v[h]===n.index&&v[h]++}return d===a[p]?!r&&v.test("")||o.push(""):o.push(a.slice(d)),o[p]>f?o.slice(0,f):o}:"0"[f](void 0,0)[p]?function(t,i){return void 0===t&&0===i?[]:e.call(this,t,i)}:e,[function(e,s){var a=t(this),n=void 0==e?void 0:e[i];return void 0!==n?n.call(e,a,s):x.call(String(a),e,s)},function(t,i){var s=u(x,t,this,i,x!==e);if(s.done)return s.value;var c=a(t),m=String(this),f=n(c,RegExp),p=c.unicode,h=(c.ignoreCase?"i":"")+(c.multiline?"m":"")+(c.unicode?"u":"")+(v?"y":"g"),_=new f(v?c:"^(?:"+c.source+")",h),C=void 0===i?g:i>>>0;if(0===C)return[];if(0===m.length)return null===o(_,m)?[m]:[];var b=0,y=0,k=[];while(y<m.length){_.lastIndex=v?y:0;var w,D=o(_,v?m:m.slice(y));if(null===D||(w=d(r(_.lastIndex+(v?0:y)),m.length))===b)y=l(m,y,p);else{if(k.push(m.slice(b,y)),k.length===C)return k;for(var S=1;S<=D.length-1;S++)if(k.push(D[S]),k.length===C)return k;y=b=w}}return k.push(m.slice(b)),k}]})},"71f3":function(t,i,e){t.exports=e.p+"img/qr.2398bca3.jpg"},ef6d:function(t,i,e){},f4cc:function(t,i,e){"use strict";e.r(i);var s=function(){var t=this,i=t.$createElement,s=t._self._c||i;return s("div",[s("van-nav-bar",{staticClass:"hader",attrs:{title:"菜谱详情","left-text":"返回","left-arrow":""},on:{"click-left":function(i){return t.back()}}},[1!=t.isiOS&&1!=t.isWeixin?s("a",{attrs:{slot:"right",href:"https://m.guanfan.top/#/app"},slot:"right"},[s("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?s("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[s("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isWeixin?s("a",{attrs:{slot:"right",href:"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU0NTg5ODQzNA==&scene=124#wechat_redirect"},slot:"right"},[s("van-button",{attrs:{type:"primary",size:"small"}},[t._v("关注")])],1):t._e()]),s("div",{staticClass:"food-img mt35",style:{backgroundImage:"url("+t.osshost+t.menuDetail.cpimg+t.detailpic+")"}}),s("div",{staticClass:"cont mt10",staticStyle:{"margin-top":"0.5rem"}},[s("div",{staticClass:"menu_info mt10"},[s("div",{staticClass:"name text-cut-two"},[t._v(t._s(t.menuDetail.title))]),s("div",{staticClass:"info clearfix"},[s("div",{staticClass:"grayColor"},[s("span",[s("van-icon",{staticClass:"icon-like2 grayColor ml10",attrs:{name:"eye"}},[t._v(t._s(t.menuDetail.visits))])],1)])])]),1!=t.isiOS&&1!=t.isWeixin?s("a",{attrs:{slot:"right",href:"https://m.guanfan.top/#/app"},slot:"right"},[s("van-button",{staticClass:"wb100 mt10 mb10",attrs:{type:"primary"}},[t._v("保存菜谱做法到手机")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?s("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[s("van-button",{staticClass:"wb100 mt10 mb10",attrs:{type:"primary"}},[t._v("保存菜谱做法到手机")])],1):t._e(),1==t.isWeixin?s("div",{staticClass:"gzh-guanzhu"},[s("img",{attrs:{src:e("71f3")}}),s("span",[t._v("长按识别二维码，关注管饭美食")])]):t._e(),s("div",[s("ul",{staticClass:"dr_list"},[s("li",{staticClass:"clearfix mb15"},[null==t.menuDetail.faceimg?s("div",{staticClass:"left headicon bg-img br50",style:{backgroundImage:"url("+t.imgurl+")"}}):t._e(),t.menuDetail.faceimg&&!t.menuDetail.isThree?s("div",{staticClass:"left headicon bg-img br50",style:{backgroundImage:"url("+t.osshost+t.menuDetail.faceimg+t.userface+")"}}):t._e(),t.menuDetail.faceimg&&t.menuDetail.isThree?s("div",{staticClass:"left headicon bg-img br50",style:{backgroundImage:"url("+t.menuDetail.faceimg+")"}}):t._e(),s("div",{staticClass:"info"},[s("h2",{staticClass:"text-bold text-df text-16"},[t._v(t._s(t.menuDetail.nickname))]),s("span",{staticClass:"grayColor text-14"},[t._v(t._s(t.menuDetail.pushtime))])]),s("i",{staticClass:"icon-like van-icon van-icon-like text-right right mt10",class:1==t.menuDetail.iscollectioned?"text-red":"",on:{click:function(i){return t.changeCollection()}}},[t._v(t._s(t.menuDetail.collections))])])]),s("div",{staticClass:"text-df"},[t._v(t._s(t.menuDetail.story))])]),s("div",{staticClass:"mt20"},[s("h2",[t._v("食材配料")]),s("div",{staticClass:"border"},t._l(t.stuff,function(i,e){return s("div",{key:e,staticClass:"clearfix text-df"},[s("span",{staticClass:"left text-bold"},[t._v(t._s(i.name))]),s("span",{staticClass:"right"},[t._v(t._s(i.num))])])}),0)]),s("div",{staticClass:"mt20"},[s("h2",[t._v("制作步骤")]),t._l(t.menuDetail.step,function(i,e){return s("div",{key:e},[s("div",{staticClass:"mainColor height-30"},[s("span",{staticClass:"text-df textTop"},[t._v("步骤")]),s("span",{staticClass:"text-xsl"},[t._v(t._s(i.sort))])]),s("div",{staticClass:"clearfix mt15"},[""!=i.stepImg?s("div",[s("div",{staticClass:"foodlist-img br5",style:{backgroundImage:"url("+t.osshost+i.stepImg+t.listpic+")"}})]):t._e(),s("div",{staticClass:"text-df"},[t._v("\n\t            "+t._s(i.description)+"\n\t          ")])])])})],2),s("div",{staticClass:"mt45"})])],1)},a=[],n=(e("28a5"),e("3b2b"),e("4917"),e("4328")),l=e.n(n),r=e("bc3a"),o=e.n(r),c={name:"cookbookinfo",data:function(){return{num:13,sortList:"",stuff:"",menuDetail:"",osshost:"http://guanfan.oss-cn-hangzhou.aliyuncs.com/",listpic:"?x-oss-process=style/list-img",userface:"?x-oss-process=style/user-img",detailpic:"?x-oss-process=style/detail-img",isWeixin:"",isiOS:"",token:"",imgurl:"../assets/img/userIcon.png",isThree:!1}},created:function(){this.cpid=this.$route.query.id,this.token=this.$store.state.user.token||"",this.getDataInfo(this.cpid),this.getwx(),this.appSource()},methods:{getwx:function(){var t=window.navigator.userAgent.toLowerCase();"micromessenger"==t.match(/MicroMessenger/i)?this.isWeixin=!0:this.isWeixin=!1},appSource:function(){var t=navigator.userAgent;navigator.appVersion;t.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)?this.isiOS=!0:this.isiOS=!1},getDataInfo:function(t){var i=this,e=l.a.stringify({cpid:t});o()({method:"post",url:"/detail/recipe",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:e}).then(function(t){if(t.data.success){i.menuDetail=t.data.result,i.menuDetail.isThree=new RegExp("http").test(i.menuDetail.faceimg),i.stuff=i.menuDetail.stuff.split("|");for(var e=0;e<i.stuff.length;e++){var s=[];s=i.stuff[e].split("#"),i.stuff[e]={name:s[0],num:s[1]}}}})},changeCollection:function(){var t=this;if(""==this.token)this.$router.push({path:"/pswLogin"});else if(1==this.menuDetail.iscollectioned){var i=l.a.stringify({itemid:this.cpid,itemtype:2});o()({method:"post",url:"/action/uncollection",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:i}).then(function(i){i.data.success&&(t.menuDetail.iscollectioned=0,t.menuDetail.collections--)})}else{var e=l.a.stringify({itemid:this.cpid,itemtype:2});o()({method:"post",url:"/action/collection",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:e}).then(function(i){i.data.success&&(t.menuDetail.iscollectioned=1,t.menuDetail.collections++)})}},back:function(){this.$router.go(-1)}}},u=c,d=(e("ffdd"),e("2877")),m=Object(d["a"])(u,s,a,!1,null,null,null);i["default"]=m.exports},ffdd:function(t,i,e){"use strict";var s=e("ef6d"),a=e.n(s);a.a}}]);
//# sourceMappingURL=chunk-25f39a2d.88dc2775.js.map