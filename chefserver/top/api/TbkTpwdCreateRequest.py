from chefserver.top.api.base import RestApi


class TbkTpwdCreateRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80, KEY=None, SECRET=None):
        RestApi.__init__(self, domain, port, KEY, SECRET)
        self.ext = None
        self.logo = None
        self.text = None
        self.url = None
        self.user_id = None

    def getapiname(self):
        return 'taobao.tbk.tpwd.create'
