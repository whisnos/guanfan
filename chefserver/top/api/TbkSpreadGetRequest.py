from chefserver.top.api.base import RestApi


class TbkSpreadGetRequest(RestApi):
    '''通用物料推荐，传入官方公布的物料id，可获取指定物料 https://open.taobao.com/api.htm?docId=33947&docType=2'''
    def __init__(self, domain='gw.api.taobao.com', port=80, KEY=None, SECRET=None):
        RestApi.__init__(self, domain, port, KEY, SECRET)
        # self.adzone_id = None
        # self.content_id = None
        # self.content_source = None
        # self.device_encrypt = None
        # self.device_type = None
        # self.device_value = None
        # self.favorites_id = None
        # self.item_id = None
        # self.material_id = None
        # self.page_no = None
        # self.page_size = None

    def getapiname(self):
        return 'taobao.tbk.spread.get'
