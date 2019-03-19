# -*- coding: utf-8 -*-

import re
import unittest


class RegexTest(unittest.TestCase):
    def setUp(self):
        pass

    def testReChinese(self):
        str = "总价262万/套起"
        price_match = re.compile(r'[\u4e00-\u9fff]+([1-9][0-9])*[\u4e00-\u9fff]+/[\u4e00-\u9fff]+')
        price_match = re.compile(r'总价([1-9][0-9]*)万/套起')
        result = price_match.match(str)
        self.assertEqual(result.group(1), "262")
