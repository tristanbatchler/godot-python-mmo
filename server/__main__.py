# Required for importing the server app (upper dir)
import sys
import pathlib
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

from server import manage
from server import models
from server import packet

from typing import Set, Optional
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

class MyServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.username: Optional[str] = None
        super().__init__()

    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        print(f"Message received: {len(payload)} bytes")
        try:
            p: packet.Packet = packet.from_json(payload.decode('utf-8'))
            print(f"Message was a valid packet object")
        except:
            print(f"Could not load message as packet.")
            if isBinary:
                print(f"Message was binary")
            else:
                print(f"Message was {payload.decode('utf8')}")
            return

        if p.action == packet.Action.Chat:
            message: str = p.payloads[0]
            if len(message) > 0:
                new_message: str = f"{self.username} says: '{message}'"
                self.broadcast(packet.ChatPacket(new_message))

        elif p.action == packet.Action.Login:
            username, password = p.payloads
            if models.User.objects.filter(username=username, password=password).exists():
                self.send_client(packet.OKPacket())
                self.username = username
                self.broadcast(packet.ChatPacket(f"{self.username} has joined."))
            else:
                self.send_client(packet.DenyPacket())

        elif p.action == packet.Action.Register:
            username, password = p.payloads
            if models.User.objects.filter(username=username).exists():
                self.send_client(packet.DenyPacket())
            else:
                models.User(username=username, password=password).save()
                self.send_client(packet.OKPacket())
            

    def onClose(self, wasClean, code, reason):
        self.factory.players.remove(self)
        print(f"{self.username}'s connection closed{' unexpectedly' if not wasClean else ' cleanly'} with code {code}: {reason}")
        self.broadcast(packet.ChatPacket(f"{self.username} has left."))

    def send_client(self, p: packet.Packet):
        b: bytes = bytes(p)
        self.sendMessage(b)
        print(f"Sent data {b}")

    def broadcast(self, p: packet.Packet):
        for other in self.factory.players:
            other.send_client(p)

        print(f"Sent {p} to all players")


class WebSocketPlayerFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        super().__init__(f"ws://{hostname}:{port}")
        self.protocol = MyServerProtocol
        self.players: Set[MyServerProtocol] = set()

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        self.players.add(p)
        return p

if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor


    log.startLogging(sys.stdout)

    PORT: int = 8081
    factory = WebSocketPlayerFactory('0.0.0.0', PORT)

    reactor.listenTCP(PORT, factory)
    reactor.run()