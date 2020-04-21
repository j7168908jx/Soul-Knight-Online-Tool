# -*- coding: utf-8 -*-
# https://blog.csdn.net/lzs781/article/details/97617723
import socket
import threading

# 端口映射配置信息
# 接收数据缓存大小
PKT_BUFF_SIZE = 16384
a_8888 = b_34444 = b_9999 = a_9999 = None

listen1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen1.bind(("0.0.0.0", 34444))


def l1():
    global a_8888, b_34444, b_9999, listen1
    while True:
        try:
            data, source = listen1.recvfrom(PKT_BUFF_SIZE)
            print('recv from 34444: {} B'.format(len(data)))
            print('listen1 data len:', len(data))
            if a_8888 is None or b_34444 is None:
                # 若有一方还未连接
                if len(data) <= 1:
                    b_34444 = source
                    print(source, 'is b34444')
                else:
                    a_8888 = source
                    print(source, 'is a8888')
            else:
                # 两方都连接了
                if source != a_8888 and source != b_34444:
                    # 有一方更换了地址
                    if source == a_8888:
                        # b换了
                        b_34444 = source
                    else:
                        # a 换了
                        a_8888 = source

            if b_34444 is not None and len(data) > 1:
                listen1.sendto(data, b_34444)
                print('send 34444 -> b34444')
            else:
                print('found no acceptor, waiting...')
        except KeyboardInterrupt:
            print('l1 stop.')
            listen1.close()
            break


listen2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen2.bind(("0.0.0.0", 8888))


def l2():
    global b_9999, a_9999, a_8888, listen1, listen2
    while True:
        try:
            data, b_9999 = listen2.recvfrom(PKT_BUFF_SIZE)
            print('recv b9999 -> 8888: {} B'.format(len(data)))

            listen1.sendto(data, a_8888)
            print('send 34444 -> a8888')
        except KeyboardInterrupt:
            print('l2 stop.')
            listen2.close()
            break


listen3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen3.bind(("0.0.0.0", 9999))


def l3():
    global a_9999, b_9999, listen2, listen3
    while True:
        try:
            data, a_9999 = listen3.recvfrom(PKT_BUFF_SIZE)
            print('recv a9999 -> 9999: {} B'.format(len(data)))

            listen2.sendto(data, b_9999)
            print('send 8888 -> b9999')

        except KeyboardInterrupt:
            print('l3 stop.')
            listen3.close()
            break


print('server start....')
t1 = threading.Thread(target=l1)
t2 = threading.Thread(target=l2)
t3 = threading.Thread(target=l3)
t1.start()
t2.start()
t3.start()
print('all server start complete')
t1.join()
t2.join()
t3.join()

listen1.close()
listen2.close()
listen3.close()

