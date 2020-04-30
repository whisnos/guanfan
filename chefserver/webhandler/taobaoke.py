from chefserver.top.api.TbkDgMaterialOptionalRequest import TbkDgMaterialOptionalRequest
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
        result = []
        # userid = self.get_session().get('id', 0)
        q = self.verify_arg_legal(self.get_body_argument('q'), '查询词', is_sensword=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        tbk_req = TbkDgMaterialOptionalRequest()
        data = {
            "adzone_id": "110317900471",
            "q": q,
            "page_no":page
        }
        res = tbk_req.getResponse(data=data)
        if res is False:
            print('无结果 尝试3')
            for i in range(1,4):
                print('第'+str(i)+'次')
                res = tbk_req.getResponse(data=data)
                if not res:
                    continue
                break
            return self.send_message('fail', 400, '获取失败，请重试.', res)

        print(8888, res['tbk_dg_material_optional_response']['result_list']['map_data'])
        result = res['tbk_dg_material_optional_response']['result_list']['map_data']
        return self.send_message('success', 0, '获取成功', result)