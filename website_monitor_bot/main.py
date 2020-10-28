import difflib
import os
import time
from typing import Any, List
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


def process_html(source_file: Path, text: str) -> List[str]:
    """
    Checks for differences between contents of a file and a provided string
    """
    with open(source_file.as_posix(), "r") as html_file:
        stored_file_content = html_file.read()
    diff = difflib.unified_diff(
        stored_file_content.splitlines(), text.splitlines(), lineterm=""
    )
    return list(diff)


def format_html_diff_message(diff_list: List[str]) -> str:
    diff_list.pop(0)
    diff_list.pop(0)
    diff_content = "\n".join(diff_list)
    return "```" + diff_content + "```"


def write_file(path: Path, content: str):
    with open(path.as_posix(), "w") as f:
        f.write(content)


def main():
    storage_file = Path(
        _env(key="STORAGE_FILE", fail=False, default="stored_file.html")
    )
    url_to_monitor = _env(key="URL_TO_MONITOR", fail=True)
    discord_webhook_url = _env(key="DISCORD_WEBHOOK_URL", fail=True)
    sleep_interval_s = int(_env(key="SLEEP_INTERVAL_S", fail=False, default="300"))
    while True:
        # Lazy "always keep going" case handling
        try:
            # Get website contents to either diff or cache for future diff'ing
            request = requests.get(url_to_monitor)

            # Check if the file is loaded, create file if not and skip checks
            if storage_file.exists() and request:
                print("found file, loading")

                # process the html content and output list of differences
                diff_list = process_html(storage_file, request.text)

                # check if diff_list has any contents and format to send to Discord if so
                # skip if no contents
                if diff_list:
                    diff_content = format_html_diff_message(diff_list)
                    print("differences found, overwriting file")
                    write_file(storage_file, request.text)
                    send_discord_message(url=discord_webhook_url, message=diff_content)
                else:
                    print("no update")
            else:
                if not request:
                    print("request failed, skipping.")
                else:
                    print(
                        "no file found, writing website contents and skipping this cycle"
                    )
                    write_file(storage_file, request.text)
        except:
            # Always just keep going in the event of an error
            pass

        # Sleep for the designated number of seconds
        time.sleep(sleep_interval_s)


if __name__ == "__main__":
    main()
