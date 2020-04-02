from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.sms import osstoken
from tornado.web import authenticated


class OssSingtureHandler(BaseHandler):
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        ''' 获取文件上传签名 '''
        file_to_object = self.verify_arg_legal(self.get_argument('type'), '上传类型', False, uchecklist=True, user_check_list=['1','2','3','4','5'])
        # 上传文件业务类型，1 上传菜谱 2 动态 3 个人头像 4 高级验证 5 主题
        # filename = self.verify_arg_legal(self.get_argument('filename'), '上传文件名', False, is_len=True, olen=38)
        filename = ''
        # print(username, password)
        code, message, result = get_singtrue_token(userid, file_to_object, filename)
        self.send_message(True, code, message, result)

def get_singtrue_token(userid, ftype, fname):
    ''' 获取oss上传签名 '''
    # code, msg, objname = get_oss_obj_name(fname)
    # if code != 0:
    #     return code, msg, objname
    if ftype == '1':
        # 菜谱
        return 0, 'ok', osstoken.get_token(str(userid) + '/caipu/')

    elif ftype == '2':
        # 动态
        return 0, 'ok', osstoken.get_token(str(userid) + '/pushimg/')

    elif ftype == '3':
        # 头像
        return 0, 'ok', osstoken.get_token(str(userid) + '/userimg/')

    elif ftype == '4':
        # 高级认证
        return 0, 'ok', osstoken.get_token(str(userid) + '/certifyimg/')

    elif ftype == '5':
        # 主题
        return 0, 'ok', osstoken.get_token(str(userid) + '/topic/')
    else:
        # 其它
        return 0, 'ok', osstoken.get_token(str(userid) + '/other/')



def get_oss_obj_name(fname):
    ''' 获取存储对象名称 '''
    # fname = "3bf59f033bc1c3444f7c54b3534045f5.jpg"
    namelist = fname.split('.')
    if len(namelist) != 2:
        return 3, '未知文件错误', None

    m5 = namelist[0].lower()
    ftype = namelist[1]
    if ftype not in ['jpg','png','jpeg','bmp']:
        return 4, '文件类型错误', None

    if len(m5) != 32:
        return 5, '文件名称错误', None
    return 0, 'ok', "/{}/{}/{}/{}.{}".format(m5[0],m5[1],m5[-1],m5,ftype)


if __name__ == '__main__':
    # res = get_oss_obj_name("3bf59f033bc1c3444f7c54b3534045f5.gif")
    # print(res)

    res = get_singtrue_token('1', "1", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', "2", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', "3", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)    
    res = get_singtrue_token('1', "4", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', "5", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)
    res = get_singtrue_token('1', "6", "3bf59f033bc1c3444f7c54b3534045f5.jpg")
    print(res)

