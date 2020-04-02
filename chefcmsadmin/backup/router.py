from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.web.login import LoginHandler, LogoutHandler, UserInfoHandler, SessionHandler
from chefcmsadmin.web.banner import BannerListHandler, BannerAddHandler, BannerDeleteHandler, BannerEditHandler
from chefcmsadmin.web.recipe import RecipeListHandler, RecipeAddHandler, RecipeDeleteHandler, RecipeEditHandler
from chefcmsadmin.web.recipestep import RecipeStepListHandler, RecipeStepAddHandler, RecipeStepDeleteHandler, RecipeStepEditHandler
from chefcmsadmin.web.classinfo import ClassInfoListHandler, ClassInfoAddHandler, ClassInfoDeleteHandler, ClassInfoEditHandler

from chefcmsadmin.web.topic import TopicSetHandler, TopicListHandler, TopicAddHandler, TopicDeleteHandler, TopicEditHandler
from chefcmsadmin.web.topic import TopicRecipeListHandler, TopicRelationAddListHandler, TopicRelationEditListHandler, TopicRelationDelListHandler

from chefcmsadmin.web.recommendrecipe import RecipeTypeSetHandler, RecipeTypeListHandler, RecipeTypeAddHandler, RecipeTypeDeleteHandler, RecipeTypeEditHandler
from chefcmsadmin.web.recommendrecipe import RecipeTypeRecipeListHandler, RecipeTypeRelationAddListHandler, RecipeTypeRelationEditListHandler, RecipeTypeRelationDelListHandler

from chefcmsadmin.web.recommendtopic import RecommendTopicListHandler, RecommendTopicAddHandler, RecommendTopicDeleteHandler, RecommendTopicEditHandler

from chefcmsadmin.web.dongtai import DongtaiListHandler, DongtaiDeleteHandler, DongtaiSetLikeHandler
from chefcmsadmin.web.report import ReportListHandler, ReportSetHandler

from chefcmsadmin.web.user import UserListHandler, UserDeleteHandler, UserCheckHandler, UserVerifyInfoHandler

from chefcmsadmin.web.campaign.campaign import CampaignAddHandler, CampaignDeleteHandler, CampaignEditHandler, CampaignListHandler, CampaignSetHandler
from chefcmsadmin.web.campaign.content import CampaignContentAddHandler, CampaignContentDeleteHandler, CampaignContentEditHandler, CampaignContentListHandler
from chefcmsadmin.web.campaign.content import CampaignJoinListHandler,CampaignJoinDeleteHandler,CampaignPkListHandler


from chefcmsadmin.web.ossserver import OssSingtureHandler
import tornado.web

class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, CMS chef!")

def make_app():
    return tornado.web.Application([
        (r"/api", MainHandler),
        (r"/api/user/login",            LoginHandler),                       # 登录
        (r"/api/user/logout",           LogoutHandler),                      # 登录
        (r"/api/user/session",          SessionHandler),                     # 会话
        (r"/api/uploadtoken",           OssSingtureHandler),                 # 获取OSS文件上传授权token
        (r"/api/banner/list",           BannerListHandler),                  # banner列表
        (r"/api/banner/add",            BannerAddHandler),                   # banner添加
        (r"/api/banner/del",            BannerDeleteHandler),                # banner删除
        (r"/api/banner/edit",           BannerEditHandler),                  # banner修改
        (r"/api/recipe/list",           RecipeListHandler),                  # recipe列表
        (r"/api/recipe/add",            RecipeAddHandler),                   # recipe添加
        (r"/api/recipe/del",            RecipeDeleteHandler),                # recipe删除
        (r"/api/recipe/edit",           RecipeEditHandler),                  # recipe修改
        (r"/api/recipestep/list",       RecipeStepListHandler),              # recipe步骤列表
        (r"/api/recipestep/add",        RecipeStepAddHandler),               # recipe步骤添加
        (r"/api/recipestep/del",        RecipeStepDeleteHandler),            # recipe步骤删除
        (r"/api/recipestep/edit",       RecipeStepEditHandler),              # recipe步骤修改
        (r"/api/class/list",            ClassInfoListHandler),               # 分类列表
        (r"/api/class/add",             ClassInfoAddHandler),                # 分类添加
        (r"/api/class/del",             ClassInfoDeleteHandler),             # 分类删除
        (r"/api/class/edit",            ClassInfoEditHandler),               # 分类修改
        (r"/api/user/list",             UserListHandler),                    # 用户列表
        (r"/api/user/del",              UserDeleteHandler),                  # 用户删除(禁用)
        (r"/api/user/checkverify",      UserCheckHandler),                   # 审核认证
        (r"/api/user/verifyinfo",       UserVerifyInfoHandler),              # 获取高级认证内容
        (r"/api/topic/list",            TopicListHandler),                   # Topic列表
        (r"/api/topic/add",             TopicAddHandler),                    # Topic添加
        (r"/api/topic/del",             TopicDeleteHandler),                 # Topic删除
        (r"/api/topic/edit",            TopicEditHandler),                   # Topic修改
        (r"/api/topic/set",             TopicSetHandler),                    # Topic设置        
        (r"/api/topic/recipelist",      TopicRecipeListHandler),             # Topic关联菜谱列表
        (r"/api/topic/recipeadd",       TopicRelationAddListHandler),        # Topic关联菜谱列表
        (r"/api/topic/recipeedit",      TopicRelationEditListHandler),       # Topic关联菜谱列表
        (r"/api/topic/recipedel",       TopicRelationDelListHandler),        # Topic关联菜谱列表
        (r"/api/recipetype/list",       RecipeTypeListHandler),              # 精品推荐列表
        (r"/api/recipetype/add",        RecipeTypeAddHandler),               # 精品推荐添加
        (r"/api/recipetype/del",        RecipeTypeDeleteHandler),            # 精品推荐删除
        (r"/api/recipetype/edit",       RecipeTypeEditHandler),              # 精品推荐修改
        (r"/api/recipetype/set",        RecipeTypeSetHandler),               # 精品推荐设置        
        (r"/api/recipetype/recipelist", RecipeTypeRecipeListHandler),        # 精品推荐关联菜谱列表
        (r"/api/recipetype/recipeadd",  RecipeTypeRelationAddListHandler),   # 精品推荐关联菜谱列表
        (r"/api/recipetype/recipeedit", RecipeTypeRelationEditListHandler),  # 精品推荐关联菜谱列表
        (r"/api/recipetype/recipedel",  RecipeTypeRelationDelListHandler),   # 精品推荐关联菜谱列表
        (r"/api/dongtai/list",          DongtaiListHandler),                 # 动态列表
        (r"/api/dongtai/del",           DongtaiDeleteHandler),               # 动态状态修改
        (r"/api/dongtai/setlike",       DongtaiSetLikeHandler),              # 动态设置点赞
        (r"/api/report/list",           ReportListHandler),                  # 举报列表
        (r"/api/report/set",            ReportSetHandler),                   # 举报状态修改
        (r"/api/recommendtopic/list",   RecommendTopicListHandler),          # 主题推荐-列表
        (r"/api/recommendtopic/add",    RecommendTopicAddHandler),           # 主题推荐-添加
        (r"/api/recommendtopic/del",    RecommendTopicDeleteHandler),        # 主题推荐-删除
        (r"/api/recommendtopic/edit",   RecommendTopicEditHandler),          # 主题推荐-编辑
        (r"/api/campaign/list",         CampaignListHandler),                # 活动-列表
        (r"/api/campaign/add",          CampaignAddHandler),                 # 活动-添加
        (r"/api/campaign/del",          CampaignDeleteHandler),              # 活动-删除
        (r"/api/campaign/edit",         CampaignEditHandler),                # 活动-编辑
        (r"/api/campaign/set",          CampaignSetHandler),                 # 活动-设置
        (r"/api/campaign/content/list", CampaignContentListHandler),         # 活动内容-列表
        (r"/api/campaign/content/add",  CampaignContentAddHandler),          # 活动内容-添加
        (r"/api/campaign/content/del",  CampaignContentDeleteHandler),       # 活动内容-删除
        (r"/api/campaign/content/edit", CampaignContentEditHandler),         # 活动内容-编辑
        (r"/api/campaign/join/list",    CampaignJoinListHandler),            # 活动参与作品列表
        (r"/api/campaign/join/del",     CampaignJoinDeleteHandler),          # 活动参与作品删除
        (r"/api/campaign/pk/list",      CampaignPkListHandler),              # 活动PK列表
        ],
        # xsrf_cookies = False,
        # xheader= True,
        # debug = True,
        # autoreload = True,
        # serve_traceback= True
    )
