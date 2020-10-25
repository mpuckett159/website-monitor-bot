website-monitor-bot

Environment variables:
STORAGE_FILE - not required, defaults to stored_file.html, can be set to whatever, probably best not to set
URL_TO_MONITOR - required, the full URL of the site you want to monitor
DISCORD_WEBHOOK_URL - required, webhook URL that is copied from the Discord channel settings
SLEEP_INTERVAL_S - not required, sets the sleep interval between website polling. Defaults to 5 minutes (300 seconds). This is set in seconds.
