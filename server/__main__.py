# Required for importing the server app (upper dir)
import sys
import pathlib
import packet
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

from server import manage, protocol
from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.internet import task, ssl
from twisted.web.static import File
from twisted.web.server import Site

class WebSocketPlayerFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        super().__init__(f"wss://{hostname}:{port}")
        self.protocol = protocol.MyServerProtocol
        self.players: set[protocol.MyServerProtocol] = set()

        # set up game tick
        self.tickrate = 10      # hertz (ticks per second)
        self.total_ticks = 0
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

        secondloop = task.LoopingCall(self.each_second)
        secondloop.start(self.tickrate)

    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        self.players.add(p)
        return p

    def tick(self):
        for p in self.players:
            p.tick()

        self.total_ticks += 1

    def each_second(self):
        for p in self.players:
            p.each_second()


if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor


    log.startLogging(sys.stdout)

    contextFactory = ssl.DefaultOpenSSLContextFactory(f'{root}/server/keys/server.key', f'{root}/server/keys/server.crt')


    PORT: int = 8081
    factory = WebSocketPlayerFactory('0.0.0.0', PORT)

    webdir = File(".")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)

    reactor.listenSSL(PORT, factory, contextFactory)
    reactor.run()