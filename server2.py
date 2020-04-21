# -*- coding: utf-8 -*-
# https://blog.csdn.net/lzs781/article/details/97617723
import socket
import threading

# 端口映射配置信息
# 接收数据缓存大小
PKT_BUFF_SIZE = 16384
a_8888 = {}
b_34444 = {}
b_9999 = {}
a_9999 = {}
recent_count = 5
listen1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen1.bind(("0.0.0.0", 34444))


def log(msg, *args, **kwargs):
    print(msg, *args, **kwargs)


def l1():
    global a_8888, b_34444, b_9999, listen1
    while True:
        try:
            data, source = listen1.recvfrom(PKT_BUFF_SIZE)
            # log('recv from 34444: {} B, '.format(len(data)))
            if len(a_8888) == 0 or len(b_34444) == 0:
                # 若至少有一方还未连接
                if len(data) == 1:
                    b_34444[source] = recent_count
                    log('b34444 found: {}'.format(source))
                else:
                    a_8888[source] = recent_count
                    log('a8888 found: {}'.format(source))
            else:
                # 两方都连接了 有一方更换了地址
                if (source not in a_8888) and (source not in b_34444):
                    if source in a_8888:
                        # b换了
                        b_34444[source] = recent_count
                        log('new b found: {}'.format(source))
                    elif source in b_34444:
                        # a 换了
                        a_8888[source] = recent_count
                        log('new a found: {}'.format(source))
                    else:
                        # 未知错误
                        a_8888[source] = recent_count
                        b_34444[source] = recent_count

                        log('**new a,b found**: {}\n\n\n'.format(source))

            if len(b_34444) != 0:

                minus(b_34444)
                for addr in b_34444:
                    b_34444[addr] = recent_count
                    listen1.sendto(data, addr)
                    # log('send 34444 -> b34444: {}'.format(addr))

                log("l1: a8888{} -> b34444{}\nall a8888:{}".format(source, b_34444, a_8888))
            else:
                log('found no acceptor, waiting...')
        except KeyboardInterrupt:
            log('l1 stop.')
            listen1.close()
            break


listen2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen2.bind(("0.0.0.0", 8888))


def l2():
    global b_9999, a_9999, a_8888, listen1, listen2
    while True:
        try:
            data, source = listen2.recvfrom(PKT_BUFF_SIZE)
            if source not in b_9999:
                b_9999[source] = recent_count
                log('b9999 found: {}'.format(source))

            # log('recv b9999 -> 8888: {} B'.format(len(data)))
            minus(a_8888)
            for addr in a_8888:
                a_8888[addr] = recent_count
                listen1.sendto(data, addr)
                # log('send 34444 -> a8888: {}'.format(addr))

            log("l2: b9999->a8888: {} -> {}\nall b9999:{} ".format(source, a_8888, b_9999))

        except KeyboardInterrupt:
            log('l2 stop.')
            listen2.close()
            break


listen3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen3.bind(("0.0.0.0", 9999))


def l3():
    global a_9999, b_9999, listen2, listen3
    while True:
        try:
            data, source = listen3.recvfrom(PKT_BUFF_SIZE)
            if source not in a_9999:
                a_9999[source] = recent_count
                log('a9999 found: {}'.format(source))

            # log('recv a9999 -> 9999: {} B'.format(len(data)))
            minus(b_9999)
            for addr in b_9999:
                b_9999[addr] = recent_count
                listen2.sendto(data, addr)
                # log('send 8888 -> b9999: {}'.format(addr))
            log("l3: a9999->b9999: {} -> {}\nall a9999:{} ".format(source, b_9999, a_9999))

        except KeyboardInterrupt:
            log('l3 stop.')
            listen3.close()
            break


def minus(a: dict):

    for key in a.keys():
        if a[key] <= 1:
            del a[key]
            continue
        a[key] -= 1



print('server start....')
t1 = threading.Thread(target=l1)
t2 = threading.Thread(target=l2)
t3 = threading.Thread(target=l3)
t1.start()
t2.start()
t3.start()
print('all server start complete')
try:
    t1.join()
    t2.join()
    t3.join()
except KeyboardInterrupt:
    print('a8888: {}'.format(a_8888))
    print('a9999: {}'.format(a_9999))
    print('b9999: {}'.format(b_9999))
    print('b34444: {}'.format(b_34444))
    pass
listen1.close()
listen2.close()
listen3.close()

