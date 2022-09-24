import os.path
import random
import shutil
from typing import Generator
import unittest
import uuid

from log_analyzer import find_log_file, render_html_report


def gen_lines(num_lines: int) -> Generator:
    """
    Generate test lines

    :param num_lines: number of lines
    :return: lines generator
    """
    flip_coin = random.choice([True, False])
    for _ in range(num_lines):
        ip = ".".join([str(random.randint(1, 256)) for _ in range(4)])
        if flip_coin:
            line = '%s - "GET /index.html HTTP/1.1" 404 42' % ip
        else:
            b = random.randint(42, 10000) if flip_coin else "-"
            line = '%s - "GET /static/%s.jpg HTTP/1.1" 200 %s' % (ip, uuid.uuid4().hex, b)
        yield line


class TestLogAnalyzer(unittest.TestCase):
    def setUp(self):
        self.log_dir_path = os.path.join(".", "TEST_LOGS")
        self.empty_log_dir_path = os.path.join(".", "EMPTY_TEST_LOGS")
        self.report_dir_path = os.path.join(".", "REPORTS")
        if not os.path.exists(self.log_dir_path) or not os.path.exists(self.empty_log_dir_path):
            os.makedirs(self.log_dir_path)
            os.makedirs(self.empty_log_dir_path)
            os.makedirs(self.report_dir_path)

        self.valid_plain_log_file = f"nginx-access-ui.log-20180606"
        self.valid_plain_log_file_path = os.path.join(self.log_dir_path, self.valid_plain_log_file)

        self.valid_gz_log_file = f"nginx-access-ui.log-20170707.gz"
        self.valid_gz_log_file_path = os.path.join(self.log_dir_path, self.valid_gz_log_file)

        self.latest_log_file = f"nginx-access-ui.log-20210707"
        self.latest_log_file_path = os.path.join(self.log_dir_path, self.latest_log_file)

        with open(self.valid_plain_log_file_path, "w") as fp:
            lines = gen_lines(100)
            for line in lines:
                fp.write(line + "\n")

        with open(self.valid_gz_log_file_path, "w") as fp:
            lines = gen_lines(100)
            for line in lines:
                fp.write(line + "\n")

        with open(self.latest_log_file_path, "w") as fp:
            lines = gen_lines(100)
            for line in lines:
                fp.write(line + "\n")

        self.report_results = [
            {'url': '/api/v2/internal/html5/phantomjs/queue/?wait=1m',
             'count': 2767,
             'count_perc': 0.10586225128874953,
             'time_sum': 174306.35200000013,
             'time_perc': 9.042900664502044,
             'time_avg': 62.994706179978365,
             'time_max': 9843.569,
             'time_med': 60.073
             },
            {'url': '/api/v2/internal/gpmd_plan_report/queue/?wait=1m&worker=5',
             'count': 1410,
             'count_perc': 0.05394498529712209,
             'time_sum': 94618.86399999996,
             'time_perc': 4.9087653910629,
             'time_avg': 67.10557730496451,
             'time_max': 9853.373,
             'time_med': 60.124
             },
            ]
        self.report_file_name = r"test_report.html"
        self.report_file_path = os.path.join(self.report_dir_path, self.report_file_name)

    def test_find_log_files_in_empty_dir(self):
        result = find_log_file(self.empty_log_dir_path)
        expected_result = None
        self.assertEqual(result, expected_result)

    def test_find_latest_log_file(self):
        file_name, _, _ = find_log_file(self.log_dir_path)
        result = file_name
        expected_result = self.latest_log_file
        self.assertEqual(result, expected_result)

    def test_render_html_report(self):
        render_html_report(report_list=self.report_results,
                           report_file_path=self.report_file_path,
                           report_template_path=r"..\report.html"
                           )
        result = False
        if self.report_file_name in os.listdir(self.report_dir_path):
            result = True

        self.assertTrue(result)

    def tearDown(self):
        shutil.rmtree(self.log_dir_path)
        shutil.rmtree(self.report_dir_path)
        os.rmdir(self.empty_log_dir_path)


if __name__ == '__main__':
    unittest.main()
