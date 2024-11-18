import asyncio
import random
import yaml
import os

from ipv8.community import CommunitySettings
from ipv8.messaging.payload_dataclass import dataclass
from ipv8.types import Peer

from cs4545.system.da_types import DistributedAlgorithm, message_wrapper


class Crash(DistributedAlgorithm):
    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
