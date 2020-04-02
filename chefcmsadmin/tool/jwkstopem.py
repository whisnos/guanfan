import six
import struct
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import jwt
import rsa
import base64

#方法二
def rsa_ne_key(e, n):
    '''
    通过rsa包依据模数和指数生成公钥，实现加密
    :param rsaExponent:
    :param rsaModulus:
    :return:
    '''
    key = rsa.PublicKey(e, n)
    return key._save_pkcs1_pem()


def intarr2long(arr):
    return int(''.join(["%02x" % byte for byte in arr]), 16)


def base64_to_long(data):
    ''' 转换 n e值 '''
    if isinstance(data, six.text_type):
        data = data.encode("ascii")
    # urlsafe_b64decode will happily convert b64encoded data
    _d = base64.urlsafe_b64decode(bytes(data) + b'==')
    return intarr2long(struct.unpack('%sB' % len(_d), _d))


def long2intarr(long_int):
    _bytes = []
    while long_int:
        long_int, r = divmod(long_int, 256)
        _bytes.insert(0, r)
    return _bytes

def long_to_base64(n):
    bys = long2intarr(n)
    data = struct.pack('%sB' % len(bys), *bys)
    if not len(data):
        data = '\x00'
    s = base64.urlsafe_b64encode(data).rstrip(b'=')
    return s.decode("ascii")


def gen_pem_by_jwks(jwson):
    '''
    通过 jwk,json格式公钥信息,生成PEM公钥
    jwson = JWKS (JSON Web 密钥集) 端点和密钥轮换
    '''
    return rsa_ne_key(base64_to_long(jwson.get('e')), base64_to_long(jwson.get('n')))


def gen_jwks_by_pem(keypem):
    '''
    通过 pem值 公钥生成 jwks
    keypem = pem公钥值 n, e值(byte类型)
    '''
    public_key = serialization.load_pem_public_key(
        keypem,
        backend=default_backend())

    public_numbers = public_key.public_numbers()
    jwks = {
        "kty": "RSA",
        "kid": "AIDOPK1",
        "use": "sig",
        "alg": "RS256",
        "n": None,
        "e": None,
    }
    jwks['n'] = long_to_base64(public_numbers.n)
    jwks['e'] = long_to_base64(public_numbers.e)
    return jwks


if __name__ == '__main__':
    jwson = {
        'n':"AQAB",
        'e':"lxrwmuYSAsTfn-lUu4goZSXBD9ackM9OJuwUVQHmbZo6GW4Fu_auUdN5zI7Y1dEDfgt7m7QXWbHuMD01HLnD4eRtY-RNwCWdjNfEaY_esUPY3OVMrNDI15Ns13xspWS3q-13kdGv9jHI28P87RvMpjz_JCpQ5IM44oSyRnYtVJO-320SB8E2Bw92pmrenbp67KRUzTEVfGU4-obP5RZ09OxvCr1io4KJvEOjDJuuoClF66AT72WymtoMdwzUmhINjR0XSqK6H0MdWsjw7ysyd_JhmqX5CAaT9Pgi0J8lU_pcl215oANqjy7Ob-VMhug9eGyxAWVfu_1u6QJKePlE-w"
    }
    keypem = gen_pem_by_jwks(jwson)
    print(keypem)
    print(gen_jwks_by_pem(keypem))