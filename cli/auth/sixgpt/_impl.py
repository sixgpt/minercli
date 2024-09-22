import requests
import vana
import os
import click
import typing as T

from eth_account.messages import encode_defunct

from constants import TMP_SIXGPT_TOKEN, SIXGPT_API, VANA_COLDKEY, VANA_HOTKEY
from miner.task import SyntheticData



def _request_challenge():
    wallet = vana.Wallet(name=VANA_COLDKEY, hotkey=VANA_HOTKEY)
    resp = requests.post(
        f"{SIXGPT_API}/auth/get-message",
        json={"walletAddress": wallet.hotkey.address},
    )
    resp.raise_for_status()
    return resp.json()["challenge"]


def _submit_signature(challenge):
    print(VANA_COLDKEY, VANA_HOTKEY)
    wallet = vana.Wallet(name=VANA_COLDKEY, hotkey=VANA_HOTKEY)
    vana.Message()
    message = encode_defunct(text=challenge["message"])
    signature = wallet.hotkey.sign_message(message).signature.hex()
    resp = requests.post(
        f"{SIXGPT_API}/auth/submit-signature",
        json={"signature": signature, "extraData": challenge["extraData"]},
    )
    resp.raise_for_status()
    return resp.json()["accessToken"]


def _get_volara_jwt() -> T.Optional[str]:
    challenge = _request_challenge()
    jwt = _submit_signature(challenge)
    return jwt


def get_sixgpt_jwt() -> T.Optional[str]:
    if os.path.exists(TMP_SIXGPT_TOKEN):
        with open(TMP_SIXGPT_TOKEN, "r") as f:
            return f.read()
    try:
        jwt = _get_volara_jwt()
    except Exception as e:
        click.echo(f"Error getting Volara JWT: {e}")
        return None
    if jwt:
        if os.path.exists(TMP_SIXGPT_TOKEN):
            os.remove(TMP_SIXGPT_TOKEN)
        with open(TMP_SIXGPT_TOKEN, "w") as f:
            f.write(jwt)
        return jwt
    click.echo("Error getting SixGPT JWT")

def submit_data(jwt: str | None, data: T.Iterable[SyntheticData]):
    if jwt is None:
        jwt = get_sixgpt_jwt()
    if jwt is None:
        click.echo("Error getting SixGPT JWT")
        return None

    # Convert SyntheticData objects to dictionaries
    data_dicts = [item.to_dict() for item in data]

    requests.post(
        f"{SIXGPT_API}/miner/submit-data",
        json={"data": data_dicts},
        headers={"Authorization": f"Bearer {jwt}"},
    )

