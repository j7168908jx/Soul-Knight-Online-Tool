# -*- coding: utf-8 -*-
# https://blog.csdn.net/lzs781/article/details/97617723
import socket
import threading
import inspect
import ctypes

raise NotImplementedError
# 端口映射配置信息
# 接收数据缓存大小
PKT_BUFF_SIZE = 16384
print('Client start....')
SERVER = input("请输入服务器地址：")


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def log(msg, *args, **kwargs):
    print(msg, *args, **kwargs)


def case_a():

    phone_ip = []
    p_game_port = []

    listen1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen1.bind(("0.0.0.0", 23333))
    listen2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen2.bind(("0.0.0.0", 8888))
    listen3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen3.bind(("0.0.0.0", 9898))

    def l1():
        while True:
            try:
                data, source = listen1.recvfrom(PKT_BUFF_SIZE)
                log('recv from game: {} B, '.format(len(data)), end='')
                if source[1] not in p_game_port or source[0] not in phone_ip:
                    p_game_port.append(source[1])
                    phone_ip.append(source[0])
                    log('phone found: {}'.format(source))

                listen2.sendto(data, (SERVER, 34444))
                log('send 8888 -> s34444')

            except KeyboardInterrupt:
                log('l1 stop.')
                listen1.close()
                break

    def l2():
        while True:
            try:
                data, source = listen2.recvfrom(PKT_BUFF_SIZE)

                log('recv s34444 -> 8888: {} B'.format(len(data)))
                for p_ip in phone_ip:
                    listen3.sendto(data, (p_ip, 7777))
                    log('send 9898 -> p7777: {}'.format((p_ip, 7777)))
            except KeyboardInterrupt:
                log('l2 stop.')
                listen2.close()
                break

    def l3():
        while True:
            try:
                data, source = listen3.recvfrom(PKT_BUFF_SIZE)
                if source[0] not in phone_ip:
                    phone_ip.append(source[0])
                    log('phone_ip found: {}'.format(source[0]))

                log('recv p7777 -> 9898: {} B, '.format(len(data)), end='')

                listen3.sendto(data, (SERVER, 9999))
                log('send 9898 -> s9999')

            except KeyboardInterrupt:
                log('l3 stop.')
                listen3.close()
                break

    return l1, l2, l3


def case_b():
    phone_ip = []
    p_game_port = []

    listen1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen1.bind(("0.0.0.0", 34444))
    listen1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    listen2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen2.bind(("0.0.0.0", 7777))
    listen3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen3.bind(("0.0.0.0", 9999))

    def l1():
        while True:
            try:
                listen1.sendto(b'\00', (SERVER, 34444))

                data, source = listen1.recvfrom(PKT_BUFF_SIZE)
                log('recv from s34444: {} B, '.format(len(data)), end='')

                listen1.sendto(data, ('255.255.255.255', 23333))
                log('send 34444 -> all23333')

            except KeyboardInterrupt:
                log('l1 stop.')
                listen1.close()
                break

    def l2():
        while True:
            try:
                data, source = listen2.recvfrom(PKT_BUFF_SIZE)
                if source[0] not in phone_ip or source[1] not in p_game_port:
                    phone_ip.append(source[0])
                    p_game_port.append(source[1])
                    log('phone found: {}'.format((phone_ip, p_game_port)))

                log('recv phone -> 7777: {} B, '.format(len(data)), end='')

                listen3.sendto(data, (SERVER, 8888))
                log('send 9999 -> s8888')
            except KeyboardInterrupt:
                log('l2 stop.')
                listen2.close()
                break

    def l3():
        while True:
            try:
                data, source = listen3.recvfrom(PKT_BUFF_SIZE)

                log('recv s8888 -> 9999: {} B, '.format(len(data)), end='')

                for ip in phone_ip:
                    for port in p_game_port:
                        listen2.sendto(data, (ip, port))
                        log('send 7777 -> phone: {}'.format((ip, port)))

            except KeyboardInterrupt:
                log('l3 stop.')
                listen3.close()
                break

    return l1, l2, l3


while True:
    game_mode = input('请输入游戏身份序号: 1为房主创建游戏，2为加入游戏')
    if game_mode == '1':
        l1, l2, l3 = case_a()
        print('可以创建游戏, 输入Ctrl-C来切换模式')
    elif game_mode == '2':
        l1, l2, l3 = case_b()
        print('可以加入游戏, 输入Ctrl-C来切换模式')
    else:
        continue

    t1 = threading.Thread(target=l1)
    t2 = threading.Thread(target=l2)
    t3 = threading.Thread(target=l3)
    t1.start()
    t2.start()
    t3.start()
    try:
        t1.join()
        t2.join()
        t3.join()
    except KeyboardInterrupt:
        pass

    stop_thread(t1)
    stop_thread(t2)
    stop_thread(t3)
