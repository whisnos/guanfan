from chefserver.webhandler.food_channel import ChannelListHandler
from chefserver.webhandler.user import LoginHandler,SendSmsHandler,RestPasswordHandler
from chefserver.webhandler.user import ModifyPhonedHandler,LogoutHandler,PersonInfoHandler
from chefserver.webhandler.user import ModifyInfoHandler, SubmitAdvancedHandler,RegisterHandler
from chefserver.webhandler.upload import UploadPhotoHandler

from chefserver.webhandler.myspace import MyspaceIndexHandler, FriendSpaceHandler, MyCaipuListIndexHandler
from chefserver.webhandler.myspace import MyfansListIndexHandler, MyfollowListIndexHandler, MyFriendListIndexHandler
from chefserver.webhandler.myspace import FollowHandler, UnFollowHandler, MyDongtaiHandler, CollectionListHandler
from chefserver.webhandler.myspace import MessageListHandler, MessageDelHandler, CaipuTempListHandler, PurchaListHandler
from chefserver.webhandler.myspace import AddPurchaHandler, DelPurchaHandler,SetPurchaBuyHandler

from chefserver.webhandler.detail import DongtaiDetailHandler, RecipeDetailHandler, RecipeEditDetailHandler
from chefserver.webhandler.detail import RecipeShowlistHandler, ReplylistHandler

from chefserver.webhandler.publish import PushRecipeHandler, PushDongtaiHandler, PushVideoDongtaiHandler, \
    EditRecipesubmitHandler, TestHandler

from chefserver.webhandler.subject import SubjectListHandler, SubjectDetailHandler

from chefserver.webhandler.action import ReplyHandler, DelReplyHandler, CollectionHandler, UnCollectionHandler
from chefserver.webhandler.action import LikeHandler, UnLikeHandler, MessageReadHandler
from chefserver.webhandler.action import MessageNumHandler, DelRecipeHandler, DelDongtaiHandler
from chefserver.webhandler.action import JubaoHandler, HeartBeatHandler
from chefserver.webhandler.action import TimeStampHandler

from chefserver.webhandler.search import SearchHandler, SearchMemberHandler, keywordHandler, SearchMomentHandler

from chefserver.webhandler.dongtaiplaza import DtPlazaHandler, DtPlazafocusHandler, DtPlazaRecommendHandler

from chefserver.webhandler.index import IndexBannerHandler, IndexRecomTopicHandler, IndexRecomRecipeHandler, \
    IndexFeaturedRecipeHandler, IndexChannelInfoAllHandler
from chefserver.webhandler.index import IndexClassInfoAllHandler

from chefserver.webhandler.ossserver import OssSingtureHandler

from chefserver.webhandler.blocklist import BlockAddHandler,BlockDelHandler,BlocklistHandler

from chefserver.webhandler.mysubject import MySubjectAddHandler,MySubjectListHandler, MySubjectDelHandler, MySubjectEditHandler
from chefserver.webhandler.mysubject import MySubjectDelRelationItemHandler, MySubjectEditHandler, MySubjectDetailHandler
from chefserver.webhandler.mysubject import MySubjectPublicListHandler

from chefserver.webhandler.campaign.campaignlist import CampaignListHandler, CampaignListAllHandler, CampaignDetailHandler, CampaignSponsorDetailHandler
from chefserver.webhandler.campaign.campaignjoin import CampaignJoinPKHandler,CampaignOpenPrizeHandler
from chefserver.webhandler.campaign.campaignjoin import CampaignRecipeListAllHandler, CampaignMomentListAllHandler

from chefserver.webhandler.authbind import AuthVerifyHandler, AuthBindHandler

from chefserver.webhandler.video.aliyunmediaapi import VideoUploadAuthKeyHandler, VideoProcessCallBackHandler


from chefserver.webhandler import basehandler
import tornado.web

class MainHandler(basehandler.BaseHandler):
    def get(self):
        # print(self.request.body, self.request.query)
        self.write("Hello, chef get!")

    def post(self):
        # print(self.request.body, self.request.query)
        self.write("Hello, chef post!")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/user/login", LoginHandler),                          # 登录
        (r"/user/register", RegisterHandler),                    # 注册
        (r"/user/logout", LogoutHandler),                        # 退出登录
        (r"/user/resetpw", RestPasswordHandler),                 # 找回密码
        (r"/user/modifyphone", ModifyPhonedHandler),             # 修改手机号
        (r"/user/personinfo", PersonInfoHandler),                # 获取个人信息
        (r"/user/sendsms", SendSmsHandler),                      # 发送SMS段
        (r"/user/modifyinfo", ModifyInfoHandler),                # 用户个人信息修改
        (r"/user/submitadvanced",SubmitAdvancedHandler),         # 提交高级验证
        (r"/uploadphoto", UploadPhotoHandler),                   # STS授权下载
        (r"/uploadphotoweb", OssSingtureHandler),                # (web)服务端签名上传下载
        (r"/myspace/index", MyspaceIndexHandler),                # 个人空间首页
        (r"/myspace/friendindex", FriendSpaceHandler),           # 好友空间首页
        (r"/myspace/cplist", MyCaipuListIndexHandler),           # 获取个人菜谱列表
        (r"/myspace/dtlist", MyDongtaiHandler),                  # 获取个人动态列表
        (r"/myspace/fanslist", MyfansListIndexHandler),          # 粉丝列表
        (r"/myspace/followlist", MyfollowListIndexHandler),      # 关注列表
        (r"/myspace/friendlist", MyFriendListIndexHandler),      # 好友列表
        (r"/myspace/follow", FollowHandler),                     # 关注
        (r"/myspace/unfollow", UnFollowHandler),                 # 取消关注
        (r"/myspace/collectionlist", CollectionListHandler),     # 收藏列表
        (r"/myspace/messagelist", MessageListHandler),           # 未删除消息列表
        (r"/myspace/messagedel", MessageDelHandler),             # 删除消息
        (r"/myspace/cptemplist", CaipuTempListHandler),          # 菜谱草稿列表
        (r"/myspace/purchalist", PurchaListHandler),             # 采购清单列表
        (r"/myspace/addpurcha", AddPurchaHandler),               # 添加采购
        (r"/myspace/delpurcha", DelPurchaHandler),               # 删除采购
        (r"/myspace/setpurcha", SetPurchaBuyHandler),            # 设置采购状态
        (r"/publish/recipe", PushRecipeHandler),                 # 发布菜谱
        (r"/publish/editrecipesubmit", EditRecipesubmitHandler), # 菜谱编辑
        (r"/publish/dongtai", PushDongtaiHandler),               # 发布图片动态
        (r"/publish/videodongtai", PushVideoDongtaiHandler),     # 发布视频动态
        (r"/detail/dongtai", DongtaiDetailHandler),              # 动态详情
        (r"/detail/recipe", RecipeDetailHandler),                # 菜谱详情
        (r"/detail/editrecipe", RecipeEditDetailHandler),        # 用户编辑菜谱详情
        (r"/detail/showlist", RecipeShowlistHandler),            # 菜谱作品秀(全部)
        (r"/detail/replylist", ReplylistHandler),                # 评论列表
        (r"/subject/topiclist", SubjectListHandler),             # 主题列表
        (r"/subject/topicdetail", SubjectDetailHandler),         # 主题详情
        (r"/action/reply", ReplyHandler),                        # 添加评论
        (r"/action/delreply", DelReplyHandler),                  # 删除评论
        (r"/action/collection", CollectionHandler),              # 收藏
        (r"/action/uncollection", UnCollectionHandler),          # 取消收藏
        (r"/action/like", LikeHandler),                          # 点赞
        (r"/action/unlike", UnLikeHandler),                      # 取消点赞
        (r"/action/msgread", MessageReadHandler),                # 消息设置已读
        (r"/action/msgnum", MessageNumHandler),                  # 获取未读消息数量
        (r"/action/delcp", DelRecipeHandler),                    # 删除菜谱
        (r"/action/deldt", DelDongtaiHandler),                   # 删除动态
        (r"/action/report", JubaoHandler),                       # 举报
        (r"/action/heartbeat", HeartBeatHandler),                # 心跳
        (r"/action/timestamp", TimeStampHandler),                # 时间戳
        (r"/dongtai/news", DtPlazaHandler),                      # 动态广场_最新最热动态
        (r"/dongtai/follownews", DtPlazafocusHandler),           # 动态广场_关注的最新动态
        (r"/dongtai/recommends", DtPlazaRecommendHandler),       # 动态广场_随机推荐动态
        (r"/search/recipe", SearchHandler),                      # 搜索菜谱
        (r"/search/moment", SearchMomentHandler),                # 搜索动态
        (r"/search/member", SearchMemberHandler),                # 搜索会员
        (r"/search/hotword", keywordHandler),                    # 返回热搜词
        (r"/index/banner", IndexBannerHandler),                  # 首页海报
        (r"/index/topic", IndexRecomTopicHandler),               # 首页推荐主题
        (r"/index/categoryrecipe", IndexRecomRecipeHandler),     # 首页精选分类菜谱
        (r"/index/featuredrecipe", IndexFeaturedRecipeHandler),  # 首页精选菜谱
        (r"/index/class", IndexClassInfoAllHandler),             # 首页分类
        (r"/index/channel", IndexChannelInfoAllHandler),         # 首页频道列表
        (r"/block/list", BlocklistHandler),                      # 黑名单列表
        (r"/block/add", BlockAddHandler),                        # 黑名单删除
        (r"/block/del", BlockDelHandler),                        # 黑名单添加
        (r"/mytopic/publiclist", MySubjectPublicListHandler),    # 个人主题公共(个人主页)列表
        (r"/mytopic/list", MySubjectListHandler),                # 个人主题列表
        (r"/mytopic/add", MySubjectAddHandler),                  # 个人主题添加
        (r"/mytopic/detail", MySubjectDetailHandler),            # 个人主题详情
        (r"/mytopic/edit", MySubjectEditHandler),                # 个人主题编辑
        (r"/mytopic/del", MySubjectDelHandler),                  # 个人主题删除
        (r"/mytopic/itemdel", MySubjectDelRelationItemHandler),  # 个人主题删除关联菜谱
        (r"/campaign/list", CampaignListHandler),                # 活动入口(首页)
        (r"/campaign/listall", CampaignListAllHandler),          # 活动列表
        (r"/campaign/detail", CampaignDetailHandler),            # 活动详情
        (r"/campaign/pk", CampaignJoinPKHandler),                # 活动PK
        (r"/campaign/cplist", CampaignRecipeListAllHandler),     # 活动最新最热食谱
        (r"/campaign/dtlist", CampaignMomentListAllHandler),     # 活动最新最热动态
        (r"/campaign/openprize", CampaignOpenPrizeHandler),      # 活动开奖
        (r"/campaign/sponsor", CampaignSponsorDetailHandler),    # 活动获取赞助商信息
        (r"/channel/detail", ChannelListHandler),                # 美食频道详情
        (r"/auth/verify", AuthVerifyHandler),                    # 第三方账号验证
        (r"/auth/bind", AuthBindHandler),                        # 第三方登录绑定验证
        (r"/uploadvideo", VideoUploadAuthKeyHandler),            # 获取视频上传凭证
        (r"/callback/vodevent", VideoProcessCallBackHandler),    # 阿里云视频事件回调
        (r"/test", TestHandler),                                 # 测试接口
        ],
        # cookie_secret = 'cb56YAgMjpevlWBNqgrv5g==',
        # login_url = '/',
        # xheader= True,
        # debug = True,
        # autoreload = True,
        # serve_traceback= True
    )