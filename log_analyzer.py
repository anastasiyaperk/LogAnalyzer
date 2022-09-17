#  !/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import logging

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": "log_analyzer.log"
    }

# logging settings
logfile_path = config["LOG_FILE"]
logger = logging.getLogger()
logging_level = logging.INFO
logger.setLevel(logging_level)
formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname).1s %(message)s',
                              datefmt='%Y.%m.%d %H:%M:%S'
                              )
if logfile_path:
    log_handler = logging.FileHandler(logfile_path)
else:
    log_handler = logging.StreamHandler()

log_handler.setLevel(logging_level)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


def main():
    pass


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', type=str, help="path to config.json")

        # Load config from file
        args = parser.parse_args()
        if args.config:
            config = json.load(args.config)

        # print(config)

    except Exception as ex:
        logger.error(ex, exc_info=True)
