#  !/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
import gzip
import json
import logging
import os
import re
from statistics import median
from string import Template
from typing import Generator, Iterable, List, Optional

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

CONFIG = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": "",
    "ERROR_THRESHOLD": 0.5,
    "REPORT_TEMPLATE_PATH": "report.html"
    }

# logging settings
logging.basicConfig(filename=CONFIG.get("LOG_FILE"),
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.INFO,
                    )
logger = logging.getLogger()


def find_log_file(logs_dir_path: str) -> Optional[tuple]:
    """
    Find the latest log file by its name

    :param logs_dir_path: path to logs directory
    :return: namedtuple with the latest log file name, extension, date. None, if logdir is empty
    """
    files = os.listdir(logs_dir_path)
    date_regexp = r"\d{8}"
    logfile_regex = f"nginx-access-ui.log-{date_regexp}(.gz)?"

    nginx_log_files = sorted([file for file in files if re.match(logfile_regex, file)], reverse=True)
    if not nginx_log_files:
        return None

    latest_logfile = nginx_log_files[0]
    date = datetime.strptime(re.search(date_regexp, latest_logfile).group(0), "%Y%m%d")
    ext = ".gz" if latest_logfile.endswith(".gz") else None

    return latest_logfile, date, ext


def log_file_reader(log_file_path: str) -> Generator:
    """
    Read log file by line

    :param log_file_path: path to reading log file
    :return: generator by lines
    """
    if log_file_path.endswith(".gz"):
        log = gzip.open(log_file_path, 'r')
    else:
        log = open(log_file_path, "r")

    for line in log:
        yield line

    log.close()


def log_parser(log_lines: Iterable, error_threshold: float) -> Optional[List[dict]]:
    """
    Parse log file and collect url statistics by request time

    :param log_lines: iterable object with log lines
    :param error_threshold: threshold of errors in parsing lines
    :return: list of dicts with statistics values
    """
    url_req_times = {}
    all_requests_time = lines_count = error_lines_count = 0

    for line in log_lines:
        line_fields = line.split()

        # TODO: Check validation more correctly
        try:
            url = line_fields[6]
            request_time = float(line_fields[-1])
        except ValueError:
            error_lines_count += 1
            continue

        all_requests_time += request_time
        lines_count += 1
        try:
            url_req_times[url].append(request_time)
        except KeyError:
            url_req_times[url] = [request_time]

    error_rate = error_lines_count / lines_count
    if error_rate >= error_threshold:
        logger.warning(
            f"Error rate exceeds the threshold value: {error_rate} (threshold = {error_threshold}). "
            f"Parsing will be finished"
            )
        return None

    results = []
    for url, req_times in url_req_times.items():
        req_count = len(req_times)
        req_time_sum = sum(req_times)
        results.append(
            {"url": url,
             "count": req_count,
             "count_perc": (req_count / lines_count) * 100,
             "time_sum": req_time_sum,
             "time_perc": (req_time_sum / all_requests_time) * 100,
             "time_avg": req_time_sum / req_count,
             "time_max": max(req_times),
             "time_med": median(req_times)
             }
            )
    # add sorting by time_sum
    results = sorted(results, key=lambda d: d['time_sum'], reverse=True)
    return results


def render_html_report(report_list: List[dict], report_file_path: str, report_template_path: str):
    """
    Create html report from list of report rows

    :param report_list: list of dicts with report rows info
    :param report_file_path: path to report file
    :param report_template_path: path to report template path
    :return:
    """
    with open(report_template_path, "r") as f:
        report_template = f.read()

    report_table_str = Template("var table = $table_json;").substitute(table_json=report_list)
    report_template = re.sub(r"var table = \$table_json;", report_table_str, report_template)

    with open(report_file_path, "w") as f:
        f.write(report_template)


def main(config_: dict):
    log_file_info = find_log_file(config_["LOG_DIR"])
    if not log_file_info:
        logger.warning(f"Log directory does not contain logs for analysis. Parsing will be finished")
        return

    file_name, date, ext = log_file_info
    report_file_name = f"report-{date.year}.{date.month}.{date.day}.html"

    if report_file_name in os.listdir(config_["REPORT_DIR"]):
        logger.info(f"Report of latest log file already exist in report dir: {report_file_name}")
        return

    logger.info(f"Latest log file is {file_name} (date: {date})")

    # Get generator with lines from the latest log file
    log_lines = log_file_reader(os.path.join(config_["LOG_DIR"], file_name))

    # Parse logs
    report_list = log_parser(log_lines, config_['ERROR_THRESHOLD'])

    # Create html report
    if report_list:
        report_file_path = os.path.join(config_["REPORT_DIR"], report_file_name)
        render_html_report(report_list[:config_["REPORT_SIZE"]], report_file_path, config_["REPORT_TEMPLATE_PATH"])
        logger.info(f"Report of latest log saved to: {report_file_path}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', type=str, help="path to config.json")

        # Load config from file
        args = parser.parse_args()
        if args.config:
            logger.info(f"Using config from file {args.config}")
            with open(args.config, 'r') as f:
                CONFIG.update(json.load(f))

        main(CONFIG)

    except Exception as ex:
        logger.error(ex, exc_info=True)
