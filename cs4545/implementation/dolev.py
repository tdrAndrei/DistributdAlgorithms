import asyncio
import random
import time
import yaml
import os
import uuid

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import dataclass
from ipv8.types import Peer

from cs4545.system.da_types import DistributedAlgorithm, message_wrapper


@dataclass
class Path:
    start: int
    path_mask: int = 0

    def add(self, node: int) -> "Path":
        return Path(self.start, self.path_mask | (1 << node))

    def contains(self, node: int) -> bool:
        return self.path_mask & (1 << node) != 0

    def node_disjoint(self, other: "Path") -> bool:
        if self.start != other.start:
            return False
        diff = self.path_mask & other.path_mask
        return diff == (1 << self.start)

    @staticmethod
    def all_disjoint(paths: list["Path"]):
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                if not paths[i].node_disjoint(paths[j]):
                    return False
        return True

    @staticmethod
    def maximum_disjoint_set(paths: list["Path"]):
        subsets = [[]]
        for index in range(0, len(paths)):
            subsets += [subset + [index] for subset in subsets]
        size = 0
        for subset in subsets[1:]:
            if Path.all_disjoint([paths[s] for s in subset]):
                size = max(size, len(subset))
        return size


@dataclass(
    msg_id=2
)  # The value 1 identifies this message and must be unique per community.
class SendMessage:
    id: str
    m: str
    path: Path


def random_id():
    return uuid.uuid4().hex


class DolevAlgorithm(DistributedAlgorithm):
    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.delivered = {}
        self.f = int(os.environ["F"])
        self.paths: dict[str, list["Path"]] = {}
        self.add_message_handler(SendMessage, self.on_message)
        self.event

    async def on_start(self):
        await super().on_start()
        print("I am dolev")
        # read some instructions for your node
        #
        # if correct node then start broadcast
        with open(os.environ["INSTRUCTIONS"], "r") as instructions_file:
            instructions = yaml.safe_load(instructions_file)
            myinstructions = instructions.get(self.node_id)
            if myinstructions is None:
                return

            to_broadcast = myinstructions.get("messages", [])
            for m in to_broadcast:
                self.broadcast(m)

    def broadcast(self, payload: str):
        msg = SendMessage(random_id(), payload, Path(self.node_id))
        for p in self.nodes.values():
            self.ez_send(p, msg)

        self.delivered[msg.id] = True
        print(f"[Delivered] {payload}")

    @message_wrapper(SendMessage)
    async def on_message(self, peer: Peer, payload: SendMessage):
        newpath = payload.path.add(self.node_id_from_peer(peer))
        if payload.id not in self.paths:
            self.paths[payload.id] = []
        self.paths[payload.id].append(newpath)

        if payload.id not in self.delivered:
            if Path.maximum_disjoint_set(self.paths[payload.id]) > self.f:
                print(f"[Delivered] {payload.m}")
                self.delivered[payload.id] = True

        for n_id, p in self.nodes.items():
            if not newpath.contains(n_id):
                msg = SendMessage(payload.id, payload.m, newpath)
                self.ez_send(p, msg)

    def ez_send(peer, msg):
        ms = random.random() * 200  # any time between 0 and 100 ms
        time.sleep(ms / 1000.0)
        super().ez_send(peer, msg)


class DolevByzantine(DolevAlgorithm):
    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)

    async def on_start(self):
        await super().on_start()
        print("I am dolev byzantine")

    @message_wrapper(SendMessage)
    async def on_message(self, peer: Peer, payload: SendMessage):
        return
