(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-8bf66444"],{"7a1e":function(t,e,r){},a40f:function(t,e,r){"use strict";r.r(e);var i=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",[r("van-nav-bar",{staticClass:"hader",attrs:{title:"登录","left-text":"返回","left-arrow":""},on:{"click-left":function(e){return t.back()}}},[1!=t.isiOS&&1!=t.isWeixin?r("a",{attrs:{slot:"right",href:"https://guanfan.oss-cn-hangzhou.aliyuncs.com/apk/guanfan_v1.0.6.apk"},slot:"right"},[r("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isiOS&&1!=t.isWeixin?r("a",{attrs:{slot:"right",href:"https://apps.apple.com/cn/app/id1487127641"},slot:"right"},[r("van-button",{attrs:{type:"primary",size:"small"}},[t._v("安装APP")])],1):t._e(),1==t.isWeixin?r("a",{attrs:{slot:"right",href:"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzU0NTg5ODQzNA==&scene=124#wechat_redirect"},slot:"right"},[r("van-button",{attrs:{type:"primary",size:"small"}},[t._v("关注")])],1):t._e()]),t._m(0),r("van-cell-group",{staticClass:"padding-lr"},[r("van-field",{attrs:{clearable:"",placeholder:"请输入手机号"},model:{value:t.ruleForm.phone,callback:function(e){t.$set(t.ruleForm,"phone",e)},expression:"ruleForm.phone"}}),r("van-field",{attrs:{clearable:"",placeholder:"请输入密码"},model:{value:t.ruleForm.password,callback:function(e){t.$set(t.ruleForm,"password",e)},expression:"ruleForm.password"}}),r("van-field",{attrs:{center:"",clearable:"",placeholder:"请输入验证码"},model:{value:t.ruleForm.verify,callback:function(e){t.$set(t.ruleForm,"verify",e)},expression:"ruleForm.verify"}},[r("van-button",{staticClass:"verBtn",attrs:{slot:"button",size:"small",type:"primary"},on:{click:function(e){return t.getCode()}},slot:"button"},[t._v(t._s(t.btnText))])],1)],1),r("div",{staticClass:"padding-lr"},[r("van-button",{staticClass:"mt15 bg-yellow",attrs:{type:"info",size:"large",disabled:!t.isSubmit},on:{click:t.signup}},[t._v("注册")]),r("van-button",{staticClass:"mt15 bg-yellow",attrs:{type:"info",size:"large",plain:""},on:{click:t.topsw}},[t._v("已有账号，去登录")])],1)],1)},n=[function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticClass:"text-center title"},[r("div",{staticClass:"text-black text-bold text-25"},[t._v("欢迎注册管饭")]),r("div",{staticClass:"grayColor text-16 mt25"},[t._v("闲来无事，就想做菜给你吃")])])}],a=(r("a481"),r("4917"),r("7ded")),s=r("d399"),o={name:"reg",data:function(){return{ruleForm:{phone:"",verify:"",password:""},btnText:"获取验证码",countdown:60,isWeixin:"",isiOS:""}},computed:{isSubmit:function(){return!!this.ruleForm.phone&&!!this.ruleForm.verify&&!!this.ruleForm.password}},created:function(){this.getwx(),this.appSource()},methods:{getwx:function(){var t=window.navigator.userAgent.toLowerCase();"micromessenger"==t.match(/MicroMessenger/i)?this.isWeixin=!0:this.isWeixin=!1},appSource:function(){var t=navigator.userAgent;navigator.appVersion;t.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)?this.isiOS=!0:this.isiOS=!1},getCode:function(){""!=this.ruleForm.phone?this.sendsms():Object(s["a"])("请输入手机号")},sendsms:function(){var t=this;Object(a["e"])(this.ruleForm.phone,2).then(function(e){var r=e.data;r.success?t.setTime():Object(s["a"])(e.message)}).catch(function(t){console.log(t)})},setTime:function(){if(0==this.countdown)return this.btnText="获取验证码",void(this.countdown=60);setTimeout(this.setTime,1e3),this.btnText="("+this.countdown+"s)后重新发送",this.countdown--},signup:function(){var t=this;Object(a["f"])(this.ruleForm).then(function(e){var r=e.data;r.success?(Object(s["a"])("注册成功"),t.$router.replace({path:"/pswLogin"})):Object(s["a"])(e.message)}).catch(function(t){console.log(t)})},topsw:function(){this.$router.replace({path:this.redirect||"/pswLogin"})},back:function(){this.$router.go(-1)}}},c=o,l=(r("ab2d"),r("2877")),u=Object(l["a"])(c,i,n,!1,null,"3af52c62",null);e["default"]=u.exports},a481:function(t,e,r){"use strict";var i=r("cb7c"),n=r("4bf8"),a=r("9def"),s=r("4588"),o=r("0390"),c=r("5f1b"),l=Math.max,u=Math.min,h=Math.floor,p=/\$([$&`']|\d\d?|<[^>]*>)/g,v=/\$([$&`']|\d\d?)/g,d=function(t){return void 0===t?t:String(t)};r("214f")("replace",2,function(t,e,r,f){return[function(i,n){var a=t(this),s=void 0==i?void 0:i[e];return void 0!==s?s.call(i,a,n):r.call(String(a),i,n)},function(t,e){var n=f(r,t,this,e);if(n.done)return n.value;var h=i(t),p=String(this),v="function"===typeof e;v||(e=String(e));var g=h.global;if(g){var b=h.unicode;h.lastIndex=0}var w=[];while(1){var x=c(h,p);if(null===x)break;if(w.push(x),!g)break;var _=String(x[0]);""===_&&(h.lastIndex=o(p,a(h.lastIndex),b))}for(var y="",k=0,S=0;S<w.length;S++){x=w[S];for(var F=String(x[0]),C=l(u(s(x.index),p.length),0),O=[],$=1;$<x.length;$++)O.push(d(x[$]));var z=x.groups;if(v){var T=[F].concat(O,C,p);void 0!==z&&T.push(z);var A=String(e.apply(void 0,T))}else A=m(F,p,C,O,z,e);C>=k&&(y+=p.slice(k,C)+A,k=C+F.length)}return y+p.slice(k)}];function m(t,e,i,a,s,o){var c=i+t.length,l=a.length,u=v;return void 0!==s&&(s=n(s),u=p),r.call(o,u,function(r,n){var o;switch(n.charAt(0)){case"$":return"$";case"&":return t;case"`":return e.slice(0,i);case"'":return e.slice(c);case"<":o=s[n.slice(1,-1)];break;default:var u=+n;if(0===u)return r;if(u>l){var p=h(u/10);return 0===p?r:p<=l?void 0===a[p-1]?n.charAt(1):a[p-1]+n.charAt(1):r}o=a[u-1]}return void 0===o?"":o})}})},ab2d:function(t,e,r){"use strict";var i=r("7a1e"),n=r.n(i);n.a}}]);
//# sourceMappingURL=chunk-8bf66444.ae1e0f09.js.map