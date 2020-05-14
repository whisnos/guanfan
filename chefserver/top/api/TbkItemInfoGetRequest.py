from chefserver.top.api.base import RestApi


class TbkItemInfoGetRequest(RestApi):
    '''https://open.taobao.com/api.htm?docId=24518&docType=2'''

    def __init__(self, domain='gw.api.taobao.com', port=80, KEY=None, SECRET=None ):
        RestApi.__init__(self, domain, port, KEY, SECRET )
        self.ip = None
        self.num_iids = None
        self.platform = None

    def getapiname(self):
        return 'taobao.tbk.item.info.get'
