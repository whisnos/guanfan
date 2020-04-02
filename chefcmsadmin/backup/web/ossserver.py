from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool import applog
from chefcmsadmin.tool import osstoken
from chefcmsadmin.config import CMS_USER_ID
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


class OssSingtureHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取文件上传签名 '''
        # file_to_object = self.verify_arg_legal(self.get_argument('type'), '上传类型', False, uchecklist=True, user_check_list=['1','2','3','4','5','6','7'])
        # 上传文件业务类型
        # filename = self.verify_arg_legal(self.get_argument('filename'), '上传文件名', False, is_len=True, olen=38)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, message, result = get_singtrue_token(arg_key.get('id', CMS_USER_ID), arg_key.get('type',90))
        self.send_cms_msg(code, message, result)

def get_singtrue_token(spaceid, ftype):
    ''' 获取oss上传签名, spaceid 通常是userid '''
    # code, msg, objname = get_oss_obj_name(fname)
    # if code != 0:
    #     return code, msg, objname
    if ftype == '1':
        # 动态
        return 0, 'ok', osstoken.get_token(spaceid + '/pushimg/')

    elif ftype == '2':
        # 菜谱
        return 0, 'ok', osstoken.get_token(spaceid + '/caipu/')

    elif ftype == '3':
        # 主题
        return 0, 'ok', osstoken.get_token(spaceid + '/topic/')

    elif ftype == '4':
        # 海报
        return 0, 'ok', osstoken.get_token(spaceid + '/banner/')

    elif ftype == '5':
        # 用户头像
        return 0, 'ok', osstoken.get_token(spaceid + '/userimg/')

    elif ftype == '6':
        # 用户高级认证
        return 0, 'ok', osstoken.get_token(spaceid + '/certifyimg/')

    elif ftype == '7':
        # 活动,格式 campaign/活动ID/图片.jpg spaceid = 活动ID
        return 0, 'ok', osstoken.get_token("campaign/" + spaceid)
    else:
        # 其它
        return 0, 'ok', osstoken.get_token(spaceid + '/other/')



def get_oss_obj_name(fname):
    ''' 获取存储对象名称 '''
    # fname = "3bf59f033bc1c3444f7c54b3534045f5.jpg"
    namelist = fname.split('.')
    if len(namelist) != 2:
        return 3, '未知文件错误', None

    m5 = namelist[0].lower()
    ftype = namelist[1]
    if ftype not in ['jpg','png']:
        return 4, '文件类型错误', None

    if len(m5) != 32:
        return 5, '文件名称错误', None
    return 0, 'ok', "/{}/{}/{}/{}.{}".format(m5[0],m5[1],m5[-1],m5,ftype)


if __name__ == '__main__':
    # res = get_oss_obj_name("3bf59f033bc1c3444f7c54b3534045f5.gif")
    # print(res)

    res = get_singtrue_token('1', 1, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', 2, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', 3, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)    
    res = get_singtrue_token('1', 4, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', 5, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', 6, "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)