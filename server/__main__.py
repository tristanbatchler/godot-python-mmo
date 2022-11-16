# Required for importing the server app (upper dir)
import sys
import pathlib
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

from server import manage, protocol
from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.internet import task

class WebSocketPlayerFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        super().__init__(f"ws://{hostname}:{port}")
        self.protocol = protocol.MyServerProtocol
        self.players: set[protocol.MyServerProtocol] = set()

        # set up game tick
        self.tickrate = 100      # hertz (ticks per second)
        self.total_ticks = 0
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        self.players.add(p)
        return p

    def tick(self):
        for p in self.players:
            p.tick()

        self.total_ticks += 1


if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor


    log.startLogging(sys.stdout)

    PORT: int = 8081
    factory = WebSocketPlayerFactory('0.0.0.0', PORT)

    reactor.listenTCP(PORT, factory)
    reactor.run()