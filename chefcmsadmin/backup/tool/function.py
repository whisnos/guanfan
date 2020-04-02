import hashlib
import uuid

def MD5encrypt(text):
    ''' md5加密 '''
    m5 = hashlib.md5(text.encode('utf-8'))
    return m5.hexdigest()


def get_uuid():
    # 获取一个随机字符串
    return str(uuid.uuid4())