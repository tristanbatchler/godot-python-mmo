import json
import enum
from json_type import *


class Action(enum.Enum):
    OK = enum.auto()
    Deny = enum.auto()
    Chat = enum.auto()
    Login = enum.auto()
    Register = enum.auto()
    Target = enum.auto()  # Player target input vector
    Pos = enum.auto()  # Player position vector
    ModelDelta = enum.auto()
    RequestFullModel = enum.auto()
    Disconnect = enum.auto()


class Packet:
    def __init__(self, action: Action, *payloads: JSONValue):
        self.action: Action = action
        self.payloads: Tuple[JSONValue] = payloads

    def __str__(self) -> str:
        serialize_dict: Dict[str, str] = {'a': self.action.name}
        for i in range(len(self.payloads)):
            serialize_dict[f'p{i}'] = self.payloads[i]
        data = json.dumps(serialize_dict, separators=(',', ':'))
        return data

    def __bytes__(self) -> bytes:
        return str(self).encode('utf-8')

    def __repr__(self) -> str:
        return str(self)

class OKPacket(Packet):
    def __init__(self):
        super().__init__(Action.OK)

class DenyPacket(Packet):
    def __init__(self):
        super().__init__(Action.Deny)

class ChatPacket(Packet):
    def __init__(self, actor_id: str, message: str):
        super().__init__(Action.Chat, actor_id, message[:80])

class LoginPacket(Packet):
    def __init__(self, username: str, password: str):
        super().__init__(Action.Login, username, password)

class RegisterPacket(Packet):
    def __init__(self, username: str, password: str, avatar_id: int):
        super().__init__(Action.Register, username, password, avatar_id)

class TargetPacket(Packet):
    def __init__(self, t_x: float, t_y: float):
        super().__init__(Action.Target, t_x, t_y)

class PosPacket(Packet):
    def __init__(self, x: float, y: float):
        super().__init__(Action.Pos, x, y)

class ModelDelta(Packet):
    def __init__(self, model_delta: dict):
        super().__init__(Action.ModelDelta, model_delta)

class RequestFullModelPacket(Packet):
    def __init__(self):
        super().__init__(Action.RequestFullModel)

class DisconnectPacket(Packet):
    def __init__(self, actor_id: int):
        super().__init__(Action.Disconnect, actor_id)

def from_json(json_str: str) -> Packet:
    obj_dict: Dict[str, str] = json.loads(json_str)

    action: Optional[Action] = None
    payloads: List[Optional[JSONValue]] = []
    for key, value in obj_dict.items():
        if key == 'a':
            action = value

        elif key[0] == 'p':
            index: int = int(key[1:])
            payloads.insert(index, value)

    # Use reflection to construct the specific packet type we're looking for
    class_name: str = action + "Packet"
    try:
        constructor: Type = globals()[class_name]
        return constructor(*payloads)
    except KeyError as e:
        print(f"KeyError: {class_name} is not a valid packet name. Stacktrace: {e}")
    except TypeError:
        print(f"TypeError: {class_name} can't handle arguments {tuple(payloads)}.")
