#!./redes2/bin/python

import socket
import selectors
import types
import time
from termcolor import colored
from threading import Timer
import atexit


lista_archivos_locales = {}
lista_archivos_remotos = {}


def start_announcements_server(host_ip, application_port):
    """
    Recibe los anuncios de archivos, los procesa y responde.
    """
    sel = selectors.DefaultSelector()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Habilitando reuso de la conexión
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Habilitando modo broadcasting
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.bind((host_ip, application_port))
    sock.setblocking(False)
    events = selectors.EVENT_READ
    sel.register(sock, events, data=None)

    # Event loop
    while True:
        events = sel.select(timeout=None) # Bloquea hasta que un socket registrado esté listo para leer/escribir
        # data, addr = sock.recvfrom(1024)
        # if data:
        #     if str(sock.type) == "SocketKind.SOCK_DGRAM":
        #         print("jsuuaj")
        #     print(data)
        #     print("Recibiendo anuncios de:", addr)
        print("mal")


def send_announcements(socket, application_port, announcements):
    if announcements:
        socket.sendto(announcements, ("<broadcast>", application_port))
        print(colored('Anunciando!', 'blue'))
        print(announce_forever.get_announcements())
    else:
        print(colored('announcements es None', 'red'))


class AnnounceForever(object):
    def __init__(self, announcements = None): 
        self._announcements = b''

    def get_announcements(self): 
        return self._announcements 

    def set_announcements(self): 
        ann = 'ANNOUNCE\n'
        for file_hash, archivo in lista_archivos_locales.items():
            ann += f'{archivo.nombre}\t{archivo.tamanio}\t{archivo.md5}\n'
        ann = ann.encode('utf-8')
        self._announcements = ann

    def start(self, socket, application_port, interval):
        # Anunciamos
        send_announcements(socket, application_port, self._announcements)
        # Armamos timer que se llama recursivamente cada interval segundos
        timer = Timer(interval, AnnounceForever.start, (self, socket, application_port, interval))
        # Registramos timer.cancel para poder parar el timer cuando el intérprete pare
        atexit.register(timer.cancel)
        timer.start()


announce_forever = AnnounceForever()

def start_announcements_client(application_port):
    """
    Hace los anuncios de archivos recurrentemente.
    Hace pedidos de anuncios
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Habilitando modo broadcasting
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    announce_forever.start(sock, application_port, 5) #TODO: poner interval correcto 30s
