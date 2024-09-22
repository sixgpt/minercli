from dataclasses import dataclass
import typing as T

import vana
from constants import NETWORK, VANA_COLDKEY, VANA_HOTKEY

@dataclass
class ChainConfig:
    network: str


def get_vana_hotkey() -> T.Optional[str]:
    try:
        config = vana.Config()
        config.chain = ChainConfig(network=NETWORK)
        wallet = vana.Wallet(name=VANA_COLDKEY, hotkey=VANA_HOTKEY)
        key = wallet.hotkey.address
        return key
    except Exception:
        return None

