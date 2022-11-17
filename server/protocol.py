# Required for importing the server app (upper dir)
import sys
import pathlib
import queue
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))
from server import models, packet

from typing import List, Optional
from autobahn.twisted.websocket import WebSocketServerProtocol
import time

class MyServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.packet_queue: queue.Queue[tuple['MyServerProtocol', packet.Packet]] = queue.Queue()
        self.actor: Optional[models.Actor] = None
        self.actor_dict: Optional[dict] = None
        self._state: Optional[callable] = None
        self._player_velocity: List[float] = [0, 0]
        self._time_last_delta: Optional[float] = None
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

    def onPacket(self, sender, p: packet.Packet):
        self.packet_queue.put((sender, p))

    def LOGIN(self, sender: 'MyServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Login:
            username, password = p.payloads
            if models.User.objects.filter(username=username, password=password).exists():
                user = models.User.objects.get(username=username)
                self.actor = models.Actor.objects.get(user=user)
                self.actor_dict = models.create_dict(self.actor)
                self._player_velocity = [0.0, 0.0]

                self.send_client(packet.OKPacket())
                self.send_client(packet.ModelDelta(models.create_dict(self.actor)))
                self.broadcast(packet.ChatPacket(f"{self.actor.get_name()} has joined."))

                self.time = None

                self._state = self.PLAY
                self.time = self.factory.total_ticks

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

        elif p.action == packet.Action.ModelDelta:
            self.send_client(p)

        elif p.action == packet.Action.Direction:
            dir_x, dir_y = p.payloads
            self._player_velocity = [dir_x * 140, dir_y * 140]  # TODO: Store speed in model and send to client

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

        if not(len(self.factory.players) == 1 and exclude_self):
            print(f"Sent {p} to {len(self.factory.players) - int(exclude_self)} protocol(s)")

    def _update_position(self, velocity: List[float], delta: float):
        dx, dy = velocity
        self.actor.instanced_entity.x += dx * delta
        self.actor.instanced_entity.y += dy * delta

    def _broadcast_actor_delta_model(self, exclude_self=False):
        updated_actor_dict: dict = models.create_dict(self.actor)
        delta_dict = models.get_delta_dict(self.actor_dict, updated_actor_dict)
        if len(delta_dict) > 2:
            self.broadcast(packet.ModelDelta(delta_dict), exclude_self=exclude_self)
            
            # Only say we've updated the actor if we've sent it to ourselves
            if not exclude_self:
                self.actor_dict = updated_actor_dict

    def tick(self):
        # Process the next packet in the queue
        if not self.packet_queue.empty():
            t = self.packet_queue.get()
            print(self._state, t)
            self._state(*t)

        # Update position
        if self._state == self.PLAY:
            now: float = time.time()
            if self._time_last_delta:
                self._update_position(self._player_velocity, now - self._time_last_delta)
            self._time_last_delta = now

            # Sync with other players as much as possible
            self._broadcast_actor_delta_model(exclude_self=True)

    def each_second(self):
        if self._state == self.PLAY:
            updated_actor_dict: dict = models.create_dict(self.actor)
            delta_dict = models.get_delta_dict(self.actor_dict, updated_actor_dict)
            if len(delta_dict) > 2:
                p = packet.ModelDelta(delta_dict)
                self.onPacket(self, p)
                print(f"Sent {p} to just my protocol")
                self.actor_dict = updated_actor_dict
