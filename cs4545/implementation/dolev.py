import asyncio
import random

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import dataclass
from ipv8.types import Peer

from cs4545.system.da_types import DistributedAlgorithm, message_wrapper


@dataclass(msg_id=1)
class BroadcastMessage:
    m: str


@dataclass(
    msg_id=2
)  # The value 1 identifies this message and must be unique per community.
class SendMessage:
    m: str
    path: list[int]  # list of node ids


class DolevAlgorithm(DistributedAlgorithm):
    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.delivered = False
        self.f = 2  # hardcoded, but get it from an env variable
        self.paths = set()
        self.add_message_handler(BroadcastMessage, self.on_broadcast)
        self.add_message_handler(SendMessage, self.on_message)

    async def on_start_as_starter(self):
        try:
            body = input("body: ")
            self.ez_send(self.nodes[self.node_id], BroadcastMessage(body))
        except EOFError:
            self.stop()

    @message_wrapper(BroadcastMessage)
    async def on_broadcast(self, peer: Peer, payload: BroadcastMessage):
        for p in self.nodes.values():
            msg = SendMessage(payload.m, [])
            self.ez_send(p, msg)
        self.delivered = True
        self.append_output(f"[Node {self.node_id}] Delivered {payload.m}")

    @message_wrapper(SendMessage)
    async def on_message(self, peer: Peer, payload: SendMessage):
        newpath = payload.path + [self.node_id_from_peer(peer)]
        self.paths.add(newpath)
        if self.delivered == False and self.paths.length == 2 * self.f + 1:
            self.append_output(f"[Node {self.node_id}] Delivered {payload.m}")
            self.delivered = True

        for p in self.nodes.values():
            if p not in newpath:
                msg = SendMessage(payload.m, newpath)
                self.ez_send(p, msg)
