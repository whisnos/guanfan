from chefserver.top.api.base import RestApi


class TbkSpreadGetRequest(RestApi):
    '''通用物料推荐，传入官方公布的物料id，可获取指定物料 https://open.taobao.com/api.htm?docId=33947&docType=2'''
    def __init__(self, domain='gw.api.taobao.com', port=80, KEY=None, SECRET=None):
        RestApi.__init__(self, domain, port, KEY, SECRET)
        self.requests = None

    def getapiname(self):
        return 'taobao.tbk.spread.get'
