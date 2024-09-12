from socket import *
import threading
from time import time, sleep


# 目的信息
server_ip = '192.168.31.7'  # input("请输入服务器ip:")
server_port = 80  # = int(input("请输入服务器port:"))


class TcpSocket:
    def __init__(self):
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)

        self.tcp_client_socket.connect((server_ip, server_port))

    def sendData(self, data, targetAddr=('192.168.31.7', 80)):
        if data == '':
            return
        data = str(data)

        def threadFunction():

            self.tcp_client_socket.send(data.encode("gbk"))
            print('Data send:', data)

            recvData = self.tcp_client_socket.recv(1024)
            print('Data received:', recvData.decode())

            return

        thread = threading.Thread(target=threadFunction)
        thread.setDaemon(True)
        thread.start()

        return thread

    def release(self):
        self.tcp_client_socket.close()


class UdpSocket:
    def __init__(self, port=3000):
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket.bind(("", port))

    def sendData(self, data, targetAddr=("192.168.31.83", 1234)):
        if data == '':
            return
        data = str(data)
        # data += f' - {time()}'

        def threadFunction():
            self.udp_client_socket.sendto(data.encode("gbk"), targetAddr)
            # print('Data send:', data)
            return

        thread = threading.Thread(target=threadFunction)
        thread.setDaemon(True)
        thread.start()

        return thread

    def close(self):
        self.udp_client_socket.close()


if __name__ == '__main__':
    # tcpSendData(input('要发送的数据为:'))
    # # while True:
    # # sendData('bed_light_toggle')
    # # sendData('lamp_light_toggle')
    # # sendData('hanging_light_toggle')
    # # input('press to end')
    udp0 = UdpSocket()
    for i in range(100):
        udp0.sendData(i)
        sleep(0.1)

    while True:
        udp0.sendData(input('Data to be send:'))

    # while len(threading.enumerate()) > 1:
    #     pass
