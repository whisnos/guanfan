(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-5bf46828"],{"28a5":function(t,i,s){"use strict";var e=s("aae3"),a=s("cb7c"),n=s("ebd6"),o=s("0390"),l=s("9def"),r=s("5f1b"),c=s("520a"),u=s("79e5"),d=Math.min,p=[].push,f="split",h="length",m="lastIndex",v=4294967295,g=!u(function(){RegExp(v,"y")});s("214f")("split",2,function(t,i,s,u){var x;return x="c"=="abbc"[f](/(b)*/)[1]||4!="test"[f](/(?:)/,-1)[h]||2!="ab"[f](/(?:ab)*/)[h]||4!="."[f](/(.?)(.?)/)[h]||"."[f](/()()/)[h]>1||""[f](/.?/)[h]?function(t,i){var a=String(this);if(void 0===t&&0===i)return[];if(!e(t))return s.call(a,t,i);var n,o,l,r=[],u=(t.ignoreCase?"i":"")+(t.multiline?"m":"")+(t.unicode?"u":"")+(t.sticky?"y":""),d=0,f=void 0===i?v:i>>>0,g=new RegExp(t.source,u+"g");while(n=c.call(g,a)){if(o=g[m],o>d&&(r.push(a.slice(d,n.index)),n[h]>1&&n.index<a[h]&&p.apply(r,n.slice(1)),l=n[0][h],d=o,r[h]>=f))break;g[m]===n.index&&g[m]++}return d===a[h]?!l&&g.test("")||r.push(""):r.push(a.slice(d)),r[h]>f?r.slice(0,f):r}:"0"[f](void 0,0)[h]?function(t,i){return void 0===t&&0===i?[]:s.call(this,t,i)}:s,[function(s,e){var a=t(this),n=void 0==s?void 0:s[i];return void 0!==n?n.call(s,a,e):x.call(String(a),s,e)},function(t,i){var e=u(x,t,this,i,x!==s);if(e.done)return e.value;var c=a(t),p=String(this),f=n(c,RegExp),h=c.unicode,m=(c.ignoreCase?"i":"")+(c.multiline?"m":"")+(c.unicode?"u":"")+(g?"y":"g"),_=new f(g?c:"^(?:"+c.source+")",m),C=void 0===i?v:i>>>0;if(0===C)return[];if(0===p.length)return null===r(_,p)?[p]:[];var b=0,y=0,w=[];while(y<p.length){_.lastIndex=g?y:0;var k,D=r(_,g?p:p.slice(y));if(null===D||(k=d(l(_.lastIndex+(g?0:y)),p.length))===b)y=o(p,y,h);else{if(w.push(p.slice(b,y)),w.length===C)return w;for(var S=1;S<=D.length-1;S++)if(w.push(D[S]),w.length===C)return w;y=b=k}}return w.push(p.slice(b)),w}]})},"71f3":function(t,i,s){t.exports=s.p+"img/qr.2398bca3.jpg"},aae3:function(t,i,s){var e=s("d3f4"),a=s("2d95"),n=s("2b4c")("match");t.exports=function(t){var i;return e(t)&&(void 0!==(i=t[n])?!!i:"RegExp"==a(t))}},ef6d:function(t,i,s){},f4cc:function(t,i,s){"use strict";s.r(i);var e=function(){var t=this,i=t.$createElement,e=t._self._c||i;return e("div",[e("van-nav-bar",{staticClass:"hader",attrs:{title:"菜谱详情","left-text":"返回","left-arrow":""},on:{"click-left":function(i){return t.back()}}},[1!=t.isiOS&&1!=t.isWeixin?e("a",{attrs:{slot:"right",href:"https://m.guanfan.top/#/app"},slot:"right"},[e("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?e("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[e("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isWeixin?e("a",{attrs:{slot:"right",href:"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU0NTg5ODQzNA==&scene=124#wechat_redirect"},slot:"right"},[e("van-button",{attrs:{type:"primary",size:"small"}},[t._v("关注")])],1):t._e()]),e("div",{staticClass:"food-img mt35",style:{backgroundImage:"url("+t.osshost+t.menuDetail.cpimg+t.detailpic+")"}}),e("div",{staticClass:"cont mt10",staticStyle:{"margin-top":"0.5rem"}},[e("div",{staticClass:"menu_info mt10"},[e("div",{staticClass:"name text-cut-two"},[t._v(t._s(t.menuDetail.title))]),e("div",{staticClass:"info clearfix"},[e("div",{staticClass:"grayColor"},[e("span",[e("van-icon",{staticClass:"icon-like2 grayColor ml10",attrs:{name:"eye"}},[t._v(t._s(t.menuDetail.visits))])],1)])])]),1!=t.isiOS&&1!=t.isWeixin?e("a",{attrs:{slot:"right",href:"https://m.guanfan.top/#/app"},slot:"right"},[e("van-button",{staticClass:"wb100 mt10 mb10",attrs:{type:"primary"}},[t._v("保存菜谱做法到手机")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?e("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[e("van-button",{staticClass:"wb100 mt10 mb10",attrs:{type:"primary"}},[t._v("保存菜谱做法到手机")])],1):t._e(),1==t.isWeixin?e("div",{staticClass:"gzh-guanzhu"},[e("img",{attrs:{src:s("71f3")}}),e("span",[t._v("长按识别二维码，关注管饭美食")])]):t._e(),e("div",[e("ul",{staticClass:"dr_list"},[e("li",{staticClass:"clearfix mb15"},[e("div",{staticClass:"left headicon bg-img br50",style:{backgroundImage:"url("+t.osshost+t.menuDetail.faceimg+t.userface+")"}}),e("div",{staticClass:"info"},[e("h2",{staticClass:"text-bold text-df text-16"},[t._v(t._s(t.menuDetail.nickname))]),e("span",{staticClass:"grayColor text-14"},[t._v(t._s(t.menuDetail.pushtime))])]),e("i",{staticClass:"icon-like van-icon van-icon-like text-right right mt10",class:1==t.menuDetail.iscollectioned?"text-red":"",on:{click:function(i){return t.changeCollection()}}},[t._v(t._s(t.menuDetail.collections))])])]),e("div",{staticClass:"text-df"},[t._v(t._s(t.menuDetail.story))])]),e("div",{staticClass:"mt20"},[e("h2",[t._v("食材配料")]),e("div",{staticClass:"border"},t._l(t.stuff,function(i,s){return e("div",{key:s,staticClass:"clearfix text-df"},[e("span",{staticClass:"left text-bold"},[t._v(t._s(i.name))]),e("span",{staticClass:"right"},[t._v(t._s(i.num))])])}),0)]),e("div",{staticClass:"mt20"},[e("h2",[t._v("制作步骤")]),t._l(t.menuDetail.step,function(i,s){return e("div",{key:s},[e("div",{staticClass:"mainColor height-30"},[e("span",{staticClass:"text-df textTop"},[t._v("步骤")]),e("span",{staticClass:"text-xsl"},[t._v(t._s(i.sort))])]),e("div",{staticClass:"clearfix mt15"},[""!=i.stepImg?e("div",[e("div",{staticClass:"foodlist-img br5",style:{backgroundImage:"url("+t.osshost+i.stepImg+t.listpic+")"}})]):t._e(),e("div",{staticClass:"text-df"},[t._v("\n\t            "+t._s(i.description)+"\n\t          ")])])])})],2),e("div",{staticClass:"mt45"})])],1)},a=[],n=(s("28a5"),s("4917"),s("4328")),o=s.n(n),l=s("bc3a"),r=s.n(l),c={name:"cookbookinfo",data:function(){return{num:13,sortList:"",stuff:"",menuDetail:"",osshost:"https://guanfan.oss-cn-hangzhou.aliyuncs.com/",listpic:"?x-oss-process=style/list-img",userface:"?x-oss-process=style/user-img",detailpic:"?x-oss-process=style/detail-img",isWeixin:"",isiOS:"",token:""}},created:function(){this.cpid=this.$route.query.id,this.token=this.$store.state.user.token||"",this.getDataInfo(this.cpid),this.getwx(),this.appSource()},methods:{getwx:function(){var t=window.navigator.userAgent.toLowerCase();"micromessenger"==t.match(/MicroMessenger/i)?this.isWeixin=!0:this.isWeixin=!1},appSource:function(){var t=navigator.userAgent;navigator.appVersion;t.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)?this.isiOS=!0:this.isiOS=!1},getDataInfo:function(t){var i=this,s=o.a.stringify({cpid:t});r()({method:"post",url:"/detail/recipe",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:s}).then(function(t){if(t.data.success){i.menuDetail=t.data.result,i.stuff=i.menuDetail.stuff.split("|");for(var s=0;s<i.stuff.length;s++){var e=[];e=i.stuff[s].split("#"),i.stuff[s]={name:e[0],num:e[1]}}}})},changeCollection:function(){var t=this;if(""==this.token)this.$router.push({path:"/pswLogin"});else if(1==this.menuDetail.iscollectioned){var i=o.a.stringify({itemid:this.cpid,itemtype:2});r()({method:"post",url:"/action/uncollection",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:i}).then(function(i){i.data.success&&(t.menuDetail.iscollectioned=0,t.menuDetail.collections--)})}else{var s=o.a.stringify({itemid:this.cpid,itemtype:2});r()({method:"post",url:"/action/collection",headers:{"Content-Type":"application/x-www-form-urlencoded",token:this.token},data:s}).then(function(i){i.data.success&&(t.menuDetail.iscollectioned=1,t.menuDetail.collections++)})}},back:function(){this.$router.go(-1)}}},u=c,d=(s("ffdd"),s("2877")),p=Object(d["a"])(u,e,a,!1,null,null,null);i["default"]=p.exports},ffdd:function(t,i,s){"use strict";var e=s("ef6d"),a=s.n(e);a.a}}]);
//# sourceMappingURL=chunk-5bf46828.33c33895.js.map