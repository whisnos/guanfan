from chefserver.top.api.base import RestApi


class TbkCouponGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80, KEY=None, SECRET=None):
        RestApi.__init__(self, domain, port, KEY, SECRET)
        self.activity_id = None
        self.item_id = None
        self.me = None

    def getapiname(self):
        return 'taobao.tbk.coupon.get'
