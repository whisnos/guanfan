from urllib import parse

# 参数区分 &
each_arg = '||_||'
# 值区分 =
each_kv = '<<_>>'

def change_byte_to_dict(bstr,querystr):
    ''' 将body字节流+query参数,转换成dict字典 '''
    # print(bstr,querystr)
    url_arg_all = ''
    body_url_str = bstr.decode('utf-8')
    # print(body_url_str)
    # qurey_url_str = querystr.decode('utf-8')

    if body_url_str !='':
        # body内容不为空
        url_arg_all += body_url_str

    if querystr!='':
        # query内容不为空
        if url_arg_all!='':
            # body + query
            url_arg_all += '&' + querystr
        else:
            # 参数 = query
            url_arg_all = querystr

    if url_arg_all=='':
        return {}

    # print(url_arg_all)
    # 在URL转换之前, 先转换 & = 为自定义符号. 确保提交的数据中的 & = 不会转成其它数据
    url_arg_all = url_arg_all.replace('&',each_arg).replace('=',each_kv)
    # real_arg_url = parse.unquotec(url_arg_all)
    # 不能用unquotec,空格会被替换成+
    real_arg_url = parse.unquote_plus(url_arg_all)
    # print(real_arg_url)
    url_dict = dict()
    # print(real_arg_url)
    for arg in real_arg_url.split(each_arg):
        kv = arg.split(each_kv);
        k,v = kv[0], kv[1]
        url_dict.setdefault(k,v)
    return url_dict
    # print(url_dict)


if __name__ == '__main__':
    s = b'title=%E8%BD%AE%E6%92%AD%E5%A4%A7%E6%B5%B7%E6%8A%A5&bannerimg=%2Fcaipu%2F4%2F0%2F6%2F409648c61dfa39f2a6d69f1551753206.jpg&linkurl=http%3A%2F%2Fwww.sina.com.cn&recipeid=50039&type=1&sort=0&status=on&id=1'
    print(change_byte_to_dict(s,''))
    b = b'title=%E8%BD%AE%E6%92%AD%E5%A4%A7%E6%B5%B7%E6%8A%A5&bannerimg=%2Fcaipu%2F4%2F0%2F6%2F409648c61dfa39f2a6d69f1551753206.jpg&linkurl=http%3A%2F%2Fwww.sina.com.cn&recipeid=50039&type=1%26%26%26%26&sort=0&status=on&id=1'
    print(change_byte_to_dict(b,''))