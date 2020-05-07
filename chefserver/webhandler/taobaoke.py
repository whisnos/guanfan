from chefserver.top.api.TbkDgMaterialOptionalRequest import TbkDgMaterialOptionalRequest
from chefserver.top.api.TbkDgOptimusMaterialRequest import TbkDgOptimusMaterialRequest
from chefserver.top.api.TbkItemInfoGetRequest import TbkItemInfoGetRequest
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog

log = applog.get_log('webhandler.taobaoke')
dbins = DbOperate.instance()


class TaoIndexSearchHandler(BaseHandler):
    ''' 我的积分 '''

    # @check_login
    async def post(self, *args, **kwargs):
        '''
        最新：
        销量："total_sales_des","total_sales_asc"
        价格："price_des","price_asc",
        返利："tk_rate_des","tk_rate_asc"
        '''
        result = []
        # userid = self.get_session().get('id', 0)
        q = self.verify_arg_legal(self.get_body_argument('q'), '查询词', is_sensword=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        sort = self.verify_arg_legal(self.get_body_argument('sort',''), '排序', False)
        tbk_req = TbkDgMaterialOptionalRequest()
        data = {
            "adzone_id": "110317900471",
            "q": q,
            "page_no": page,
            "sort": sort
        }
        res = await tbk_req.getResponse(data=data)
        # if res is False:
        #     print('无结果 尝试3')
        #     res=await tbk_req.repeat_try(data=data)
        # for i in range(1,4):
        #     res = await tbk_req.getResponse(data=data)
        #     if res:
        #         break

        if not res:
            return self.send_message('fail', 400, '获取失败，请重试.', res)
        result = res['tbk_dg_material_optional_response']['result_list']['map_data']
        return self.send_message('success', 0, '获取成功', result)

class TaoIndexChannelInfoAllHandler(BaseHandler):
    ''' 返回所有分类 '''
    async def get(self):
        success, code, message, result = await get_all_channel()
        return self.send_message(success, code, message, result)


async def get_all_channel():
    ''' 获取所有分类 '''
    classinfo_sql = '''
select id,name,type,iconImg,pid_id,materialId,sort
from tao_channel_info
order by sort desc
'''
    classinfo_result = await dbins.select(classinfo_sql, ())
    if classinfo_result is None:
        return False, 3001, '获取列表错误,错误的内容', None

    # print(classinfo_result[:5])

    result_tp01 = []

    for info1 in classinfo_result:
        # 一级分类
        if info1.get('type') == 1:
            # print(info1)
            info_1_tmp = dict()
            info_1_tmp = info1.copy()
            info_1_tmp.setdefault('childlist', [])
            result_tp01.append(info_1_tmp)

    result_tp02 = []
    for info2 in classinfo_result:
        # 二级分类
        if info2.get('type') == 2:
            info_2_tmp = dict()
            info_2_tmp = info2.copy()
            info_2_tmp.setdefault('childlist', [])
            # info2.setdefault('childlist', [])
            result_tp02.append(info_2_tmp)

    for info3 in classinfo_result:
        # 三级分类,添加到2级分类子目录
        if info3.get('type') == 3:
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
        tbk_req = TbkDgOptimusMaterialRequest()
        data = {
            "adzone_id": "110317900471",
            "material_id": mid,
            "page_no": page,
        }
        res = await tbk_req.getResponse(data=data)
        if not res:
            return self.send_message('fail', 400, '获取失败，请重试.', res)
        result = res['tbk_dg_optimus_material_response']['result_list']['map_data']
        return self.send_message('success', 0, '获取成功', result)



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
            return self.send_message('fail', 400, '获取失败，请重试.', res)
        result = res['tbk_item_info_get_response']['results']['n_tbk_item']
        return self.send_message('success', 0, '获取成功', result)
