# Required for importing the server app (upper dir)
import sys
import pathlib
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))
from server import models, packet

from typing import List, Optional
from autobahn.twisted.websocket import WebSocketServerProtocol

class MyServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.actor: Optional[models.Actor] = None
        self._state: Optional[callable] = None
        self._player_velocity: List[float] = [0, 0]
        super().__init__()

    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")
        self._state = self.LOGIN

    def onMessage(self, payload, isBinary):
        print(f"Message received: {len(payload)} bytes")
        try:
            p: packet.Packet = packet.from_json(payload.decode('utf-8'))
            print(f"Message was a valid packet object")
        except Exception as e:
            print(f"Could not load message as packet: {e}")
            if isBinary:
                print(f"Message was binary")
            else:
                print(f"Message was {payload.decode('utf8')}")
            return

        self.onPacket(self, p)
            
    def onPacket(self, sender: 'MyServerProtocol', p: packet.Packet):
        self._state(sender, p)

    def LOGIN(self, sender: 'MyServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Login:
            username, password = p.payloads
            if models.User.objects.filter(username=username, password=password).exists():
                user = models.User.objects.get(username=username)
                self.actor = models.Actor.objects.get(user=user)
                self._player_velocity = [0.0, 0.0]

                self.send_client(packet.OKPacket())
                self.send_client(packet.ModelDelta(models.create_dict(self.actor)))
                self.broadcast(packet.ChatPacket(f"{self.actor.get_name()} has joined."))

                self._state = self.PLAY

            else:
                self.send_client(packet.DenyPacket())

        elif p.action == packet.Action.Register:
            username, password = p.payloads
            if models.User.objects.filter(username=username).exists():
                self.send_client(packet.DenyPacket())
            else:
                user = models.User(username=username, password=password)
                user.save()
                player_entity = models.Entity(name=username)
                player_entity.save()
                player_ientity = models.InstancedEntity(entity=player_entity, x=0, y=0)
                player_ientity.save()
                inventory_entity = models.Entity(name=f"{player_entity.name}'s inventory")
                inventory_entity.save()
                inventory_ientity = models.InstancedEntity(entity=inventory_entity, x=player_ientity.x, y=player_ientity.y)
                inventory_ientity.save()
                inventory_container = models.Container(instanced_entity=inventory_ientity)
                inventory_container.save()
                player = models.Actor(instanced_entity=player_ientity, inventory=inventory_container, user=user)
                player.save()
                self.send_client(packet.OKPacket())

    def PLAY(self, sender: 'MyServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Chat:
            message: str = p.payloads[0]
            if len(message) > 0:
                new_message: str = f"{sender.actor.get_name()} says: '{message}'"
                new_packet: packet.ChatPacket = packet.ChatPacket(new_message)
                if sender == self:
                    self.broadcast(new_packet, exclude_self=True)
                self.send_client(new_packet)

        elif p.action == packet.Action.Direction:
            dir_x, dir_y = p.payloads
            self._player_velocity = [dir_x * 200.0, dir_y * 200.0]  # TODO: Store speed in model and send to client
            
            # If the player has stopped, send them their position so the client can
            # interpolate and sync up
            if p.payloads == (0, 0):
                self.send_client(packet.ModelDelta(models.create_dict(self.actor)))

    def onClose(self, wasClean, code, reason):
        self.factory.players.remove(self)
        print(f"Websocket connection closed{' unexpectedly' if not wasClean else ' cleanly'} with code {code}: {reason}")
        if self._state == self.PLAY:
            self.broadcast(packet.ChatPacket(f"{self.actor.get_name()} has left."), exclude_self=True)

    def send_client(self, p: packet.Packet):
        b: bytes = bytes(p)
        self.sendMessage(b)
        print(f"Sent data {b}")

    def broadcast(self, p: packet.Packet, exclude_self: bool = False):
        for other in self.factory.players:
            if other == self and exclude_self:
                continue
            other.onPacket(self, p)

        print(f"Sent {p} to all protocols")

    def _update_position(self, velocity: List[float]):
        dx, dy = velocity
        self.actor.instanced_entity.x += dx / self.factory.tickrate
        self.actor.instanced_entity.y += dy / self.factory.tickrate

    def tick(self):
        if self._state == self.PLAY:
            self._update_position(self._player_velocity)
        