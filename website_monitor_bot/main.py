import difflib
import os
import time
from typing import Any
from pathlib import Path

import requests
from discord_webhook import DiscordWebhook


def send_discord_message(url: str, message: str) -> None:
    print("sending update message to Discord channel")
    webhook = DiscordWebhook(url=url, content=message)
    webhook.execute()


def _env(
    key: str,
    fail: bool = True,
    default: Any = None,
) -> Any:
    """
    Function used to read container/OS environmnet variables in and return the
    values to be stored in global Python variables.
    """
    value = os.environ.get(key)
    if value is None:
        if fail and default is None:
            raise KeyError(f"Key '{key}' is not present in environment!")
        value = default
    return value


def main():
    storage_file = Path(
        _env(key="STORAGE_FILE", fail=False, default="stored_file.html")
    )
    url_to_monitor = _env(key="URL_TO_MONITOR", fail=True)
    discord_webhook_url = _env(key="DISCORD_WEBHOOK_URL", fail=True)
    sleep_interval_s = int(_env(key="SLEEP_INTERVAL_S", fail=False, default="300"))
    while True:
        request = None
        try:
            request = requests.get(url_to_monitor)
        except:
            pass
        if storage_file.exists() and request:
            print("found file, loading")
            with open(storage_file.as_posix(), "r") as f:
                stored_file_content = f.read()
            diff = difflib.unified_diff(stored_file_content.splitlines(), request.text.splitlines(), lineterm="")
            diff_content = "\n".join(diff)
            if diff_content:
                diff_content = "```"+diff_content+"```"
                print("differences found, overwriting file")
                if storage_file.exists():
                    storage_file.unlink()
                with open(storage_file.as_posix(), "w") as f:
                    f.write(request.text)
                send_discord_message(url=discord_webhook_url, message=diff_content)
            else:
                print("no update")
        else:
            if not request:
                print("request failed, skipping.")
            else:
                print("no file found, writing website contents and skipping this cycle")
                with open(storage_file.as_posix(), "w") as f:
                    f.write(request.text)
        time.sleep(sleep_interval_s)


if __name__ == "__main__":
    main()
