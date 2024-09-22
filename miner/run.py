import asyncio
import logging
import os

import miner.dlp.volara as volara
from constants import (
    ERROR_SLEEP_INTERVAL,
    TARGET_EXAMPLE_COUNT,
    TIMELINE_SLEEP_INTERVAL,
    TMP_MINER_LOG,
    MODEL_NAME
)
from miner.build import build_buffer, build_zip_buffer
from miner.extract import SyntheticData 
from miner.drive import write_uuid_file
from cli.auth.openai import get_active_account, set_active_account
from openai import OpenAI
from miner.task import WikipediaSummarization
import cli.auth.sixgpt as sixgpt_auth


logger = logging.getLogger(__name__)

async def start_mining():
    logger.info("Starting mining...")
    client = get_active_account()
    if client is None:
        result = set_active_account()
        if not result:
            logger.error("Failed to set active openai account. Exiting..")
            return
        client = get_active_account()
        if client is None:
            logger.error("OpenAI client not found. Exiting..")
            return
    jwt = sixgpt_auth.get_sixgpt_jwt()
    if jwt is None:
        logger.error("Failed to get sixgpt jwt. Exiting..")
        return

    task = WikipediaSummarization(client)

    while True:
        examples: set[SyntheticData] = set()
        while len(examples) < TARGET_EXAMPLE_COUNT:
            logger.info("Generating completion:")

            try:
                example = task.run()
            except Exception:
                logger.exception("Error generating dataset")
                logger.info(f"Sleeping {ERROR_SLEEP_INTERVAL}s for next attempt...")
                await asyncio.sleep(ERROR_SLEEP_INTERVAL)
                continue
            examples.add(example)
            logger.info(
                f"Pulled {example.context['title']}... total buffer: {len(examples)}"
            )
            if len(examples) >= TARGET_EXAMPLE_COUNT:
                break
            await asyncio.sleep(TIMELINE_SLEEP_INTERVAL)
        tweet_buffer = build_buffer(examples)
        logger.info("Uploading tweet buffer to drive...")
        zip_buffer = build_zip_buffer(tweet_buffer)
        file_url = await write_uuid_file(zip_buffer)
        logger.info(f"Uploaded examples buffer to {file_url}")
        logger.info("Submitting to sixgpt...")
        await volara.submit(file_url)
        sixgpt_auth.submit_data(jwt, examples)
        logger.info("Submitted to sixgpt.")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(TMP_MINER_LOG), exist_ok=True)
    try:
        os.remove(TMP_MINER_LOG)
    except FileNotFoundError:
        pass
    output_handler = logging.FileHandler(TMP_MINER_LOG)
    logger.setLevel(logging.INFO)
    logger.addHandler(output_handler)
    try:
        asyncio.run(start_mining())
    except Exception:
        logger.exception("Exception encountered")
        logger.info("Exiting...")
