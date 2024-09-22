import flatbuffers
import zipfile
import io
import typing as T
import json

from miner.extract import SyntheticData


def build_buffer(examples: T.Iterable[SyntheticData]) -> bytes:
    return json.dumps([example.to_dict() for example in examples]).encode('utf-8')


def build_zip_buffer(buffer: bytes) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("examples.data", buffer)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
