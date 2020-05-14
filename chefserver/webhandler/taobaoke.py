from playhouse.shortcuts import model_to_dict

from chefserver.config import TAO_APP_KEY, TAO_APP_SECRET, TAO_APP_KEY_ANDROID, TAO_APP_SECRET_ANDROID, PAGE_SIZE
from chefserver.models.tbk import Tao_Promote_Info, Tao_Collect_Info, Tao_Banner_Info
from chefserver.top.api.TbkCouponGetRequest import TbkCouponGetRequest
from chefserver.top.api.TbkDgMaterialOptionalRequest import TbkDgMaterialOptionalRequest
from chefserver.top.api.TbkDgOptimusMaterialRequest import TbkDgOptimusMaterialRequest
from chefserver.top.api.TbkItemInfoGetRequest import TbkItemInfoGetRequest
from chefserver.top.api.TbkSpreadGetRequest import TbkSpreadGetRequest
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog

log = applog.get_log('webhandler.taobaoke')
dbins = DbOperate.instance()


class TaoIndexSearchHandler(BaseHandler):
    ''' 淘宝客搜索 '''

    # @check_login
    async def post(self, *args, **kwargs):
        '''
        最新：
        销量："total_sales_des","total_sales_asc"
        价格："price_des","price_asc",
        返利："tk_rate_des","tk_rate_asc"
        '''
        q = self.verify_arg_legal(self.get_body_argument('q'), '查询词', is_sensword=True)
        page = self.verify_arg_num(self.get_body_argument('page'), '页数', is_num=True)
        sort = self.verify_arg_legal(self.get_body_argument('sort', ''), '排序', False)
        client = self.verify_arg_num(self.get_body_argument('client'), '客户端类型', is_num=True, ucklist=True,
                                   user_check_list=['0', '1'])

        # type = self.verify_arg_num(self.get_body_argument('type'), '足迹 or 收藏', is_num=True, ucklist=True,
        #                            user_check_list=['0', '1'])
        # 获取推广位
        status, adzone_id, tbk_req = await check_tbk_promote(self, client, TbkDgMaterialOptionalRequest, True,)
        if not status:
            return self.send_msg(False, 400, '推广位获取失败，请重试.', '')
        data = {
            "adzone_id": adzone_id,
            "q": q,
            "page_no": str(page),
            "sort": sort,
            "has_coupon": "true",
        }
        res = await tbk_req.getResponse(data=data)
        if not res:
            return self.send_msg(False, 400, '商品获取失败，请重试.', res)
        result = res['tbk_dg_material_optional_response']['result_list']['map_data']
        return self.send_msg('success', 0, '获取成功', result)


async def check_tbk_promote(self,client, TbkRequest, is_promote,):
    '''获取tbk推广位'''
    adzone_id = ''
    if is_promote:
        promote_query = Tao_Promote_Info.select().where(Tao_Promote_Info.type == client).order_by(
            Tao_Promote_Info.id.desc()).limit(1)
        exchanges_warpper = await self.application.objects.execute(promote_query)
        if exchanges_warpper:
            for ex in exchanges_warpper:
                adzone_id = ex.promoteID
                print('adzone_id',adzone_id)
        else:
            return False, '', ''

    if client == 0:
        tbk_req = TbkRequest(KEY=TAO_APP_KEY, SECRET=TAO_APP_SECRET)
    elif client == 1:
        tbk_req = TbkRequest(KEY=TAO_APP_KEY_ANDROID, SECRET=TAO_APP_SECRET_ANDROID)
    else:
        return False, '', ''

    return True, adzone_id, tbk_req


class TaoIndexChannelInfoAllHandler(BaseHandler):
    ''' 返回所有分类 '''

    async def get(self):
        success, code, message, result = await get_all_channel()
        return self.send_message(success, code, message, result)


async def get_all_channel():
    ''' 获取所有分类 '''
    classinfo_sql = '''
select id,name,level,iconImg,pid_id,materialId,recommendId,is_banner,sort
from tao_channel_info
where status=0 order by sort desc
'''
    classinfo_result = await dbins.select(classinfo_sql, ())
    if not classinfo_result:
        return False, 404, '列表数据为空', None

    # print(classinfo_result[:5])

    result_tp01 = []

    for info1 in classinfo_result:
        # 一级分类
        if info1.get('level') == 1:
            # print(info1)
            info_1_tmp = dict()
            info_1_tmp = info1.copy()
            info_1_tmp.setdefault('childlist', [])
            result_tp01.append(info_1_tmp)

    result_tp02 = []
    for info2 in classinfo_result:
        # 二级分类
        if info2.get('level') == 2:
            info_2_tmp = dict()
            info_2_tmp = info2.copy()
            info_2_tmp.setdefault('childlist', [])
            # info2.setdefault('childlist', [])
            result_tp02.append(info_2_tmp)

    for info3 in classinfo_result:
        # 三级分类,添加到2级分类子目录
        if info3.get('level') == 3:
            for rtp2 in result_tp02:
                if rtp2.get('id') == info3.get('pid_id'):
                    # info_3_tmp = dict()
                    # info_3_tmp = info3.copy()
                    rtp2.get('childlist').append(info3)

    for crtp2 in result_tp02:
        # 二级分类添加到根目录
        for rtp1 in result_tp01:
            if rtp1.get('id') == crtp2.get('pid_id'):
                rtp1.get('childlist').append(crtp2)
    return True, 0, 'success', result_tp01


class TaoIndexMaterialSearchAllHandler(BaseHandler):
    ''' 物料id搜索 '''

    async def post(self, *args, **kwargs):
        '''
        '''
        mid = self.verify_arg_legal(self.get_body_argument('mid'), '物料id', is_sensword=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        # sort = self.verify_arg_legal(self.get_body_argument('sort',''), '排序', False)
        client = self.verify_arg_num(self.get_body_argument('client'), '客户端类型', is_num=True, ucklist=True,
                                   user_check_list=['0', '1'])
        # 获取推广位

        status, adzone_id, tbk_req = await check_tbk_promote(self, client, TbkDgOptimusMaterialRequest,True)
        if not status:
            return self.send_msg(False, 400, '推广位获取失败，请重试.', '')

        data = {
            "adzone_id": adzone_id,
            "material_id": mid,
            "page_no": page,
        }
        res = await tbk_req.getResponse(data=data)
        if not res:
            return self.send_message(False, 400, '获取失败，请重试.', res)
        result = res['tbk_dg_optimus_material_response']['result_list']['map_data']
        return self.send_message(True, 0, '获取成功', result)


class TaoIndexItemInfoAllHandler(BaseHandler):
    ''' 物料id搜索 '''

    async def post(self, *args, **kwargs):
        '''
        '''
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '物料id', is_sensword=True)
        tbk_req = TbkItemInfoGetRequest()
        data = {
            "num_iids": itemid,
        }
        res = await tbk_req.getResponse(data=data)
        if not res:
            return self.send_message(False, 400, '获取失败，请重试.', res)
        result = res['tbk_item_info_get_response']['results']['n_tbk_item']
        tbk_coupon_req = TbkCouponGetRequest()
        data1 = {
            "item_id": itemid,
            # "me":'giH3mq9EcIOjmZ7U4RgGFXeM9yGNF6KAXUML6bImjAWW5fft0zJPvhS9BWurN9lCiq3nJybq329ssTiAJ6qTjpM8HzIryGxc1U7LypH9IemyKazIKfzoh9y7PUDQgHNf3',
            "activity_id": "2d2ae6fbe1af4869ac7f1d79ca9fb9e7"
        }
        coupon_res = await tbk_coupon_req.getResponse(data=data1)
        result.appent()
        return self.send_message(True, 0, '获取成功', result)

import urllib.parse
class TaoFootPrintAllHandler(BaseHandler):
    '''足迹'''

    @check_login
    async def get(self):
        userid = self.get_session().get('id', 0)
        page = self.verify_arg_num(self.get_argument('page'), '页数', is_num=True)
        type = self.verify_arg_num(self.get_argument('type'), '足迹 or 收藏', is_num=True, ucklist=True,
                                   user_check_list=['0', '1'])
        client = self.verify_arg_num(self.get_argument('client'), '客户端类型', is_num=True, ucklist=True,
                                     user_check_list=['0', '1'])
        collect_query = Tao_Collect_Info.select().where(Tao_Collect_Info.user_id==userid, Tao_Collect_Info.type==type,Tao_Collect_Info.status==0).paginate(int(page), PAGE_SIZE)
        collects_wrappers = await self.application.objects.execute(collect_query)
        if not collects_wrappers:
            return self.send_msg(False, 400, '没有产品.', '')
        item_list = []
        item_dict ={}
        for wrap in collects_wrappers:
            item_list.append(wrap.itemId)
            item_dict[wrap.itemId]=wrap.createTime.strftime('%Y-%m-%d %H:%M:%S')
            item_dict[str(wrap.itemId)+"Id"] = wrap.id
            item_dict[str(wrap.itemId) + "Content"] = wrap.content
        new_str = ','.join(item_list)
        # 进行批量请求淘宝数据
        status, adzone_id, tbk_req = await check_tbk_promote(self, client, TbkItemInfoGetRequest,False)
        if not status:
            return self.send_msg(False, 400, '获取失败，请重试.', '')

        data = {
            "num_iids": new_str,
        }
        res = await tbk_req.getResponse(data=data)
        if not res:
            return self.send_message(False, 400, '获取失败，请重试.', False)
        result = res['tbk_item_info_get_response']['results']['n_tbk_item']
        for item in result:
            item_time = item_dict[str(item['num_iid'])]
            item['createTime']=item_time
            item['id'] = item_dict[str(item['num_iid'])+"Id"]
            item['coupon_share_url'] = item_dict[str(item['num_iid']) + "Content"]
        return self.send_message(True, 0, '操作成功', result)

    @check_login
    async def post(self):
        result = []
        userid = self.get_session().get('id', 0)
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '商品id', False, )
        coupon_share_url = self.verify_arg_legal(self.get_body_argument('coupon_share_url'), '商品二合一链接', False, )
        type = self.verify_arg_num(self.get_body_argument('type'), '足迹 or 收藏', is_num=True, ucklist=True,
                                   user_check_list=['0', '1'])
        data_dict = {
            "user_id": userid,
            "itemId": itemid,
            "type": type,
            "content":""
        }
        try:
            collect_obj = await self.application.objects.get(Tao_Collect_Info, user_id=userid, itemId=itemid,
                                                                type=type, status=0)
            await self.application.objects.delete(collect_obj)
        except Tao_Collect_Info.DoesNotExist:
            pass
        # 转链处理
        tbk_req = TbkSpreadGetRequest(KEY=TAO_APP_KEY, SECRET=TAO_APP_SECRET)
        url = "http:"+coupon_share_url
        s = urllib.parse.unquote(url)
        tbk_req.requests = [{"url": s}]
        res = await tbk_req.getResponse()
        if 'domain is not support' in str(res):
            for i in range(1, 4):
                res = await tbk_req.getResponse()
                if 'domain is not support' not in str(res):
                    data_dict['content']=res['tbk_spread_get_response']['results']['tbk_spread'][0]['content']
        if 'domain is not support' not in str(res):
            data_dict['content'] = res['tbk_spread_get_response']['results']['tbk_spread'][0]['content']
        else:
            data_dict["content"] = s
        await self.application.objects.create(Tao_Collect_Info, **data_dict)

        return self.send_message(True, 0, '操作成功', result)

    @check_login
    async def delete(self, *args, **kwargs):
        result = []
        userid = self.get_session().get('id', 0)
        did = self.get_body_argument('did','')
        alldelete = self.get_body_argument('alldelete','')
        type = self.get_body_argument('type','')
        if did:
            try:
                collect_obj = await self.application.objects.get(Tao_Collect_Info, id=did, status=0)
                collect_obj.status = -1
                await self.application.objects.update(collect_obj)
            except Tao_Collect_Info.DoesNotExist:
                return self.send_message(False, 404, '操作对象不存在', result)
        if alldelete and type:
            collect_query = Tao_Collect_Info.select().where(Tao_Collect_Info.user_id == userid,
                                                            Tao_Collect_Info.type == int(type),
                                                            Tao_Collect_Info.status == 0)
            collects_wrappers = await self.application.objects.execute(collect_query)
            for wrap in collects_wrappers:
                wrap.status = -1
                await self.application.objects.update(wrap)
        return self.send_message(True, 0, '操作成功', result)


class TaoBannerAllHandler(BaseHandler):
    '''轮播图'''

    async def get(self):
        banner_query = Tao_Banner_Info.select().order_by(Tao_Banner_Info.sort.desc()).where(Tao_Banner_Info.status==0)
        banners_wrappers = await self.application.objects.execute(banner_query)
        if not banners_wrappers:
            return self.send_msg(False, 400, '没有轮播图', False)
        result = []
        for wrap in banners_wrappers:
            banner_dict = model_to_dict(wrap)
            ct = banner_dict.get('createTime', None)
            if ct:
                banner_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
            result.append(banner_dict)
        return self.send_message(True, 0, '获取成功', result)