#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" script for testing the script openstriato.py
"""

import os

class TestOpenSriato(object):
    """
    Test the openstriato commands
    """
    def __init__(self):
        """ initialization procedures when initializing the class
        """
        pass

    def setUp(self):
        """ add here functions to call before starting the test
        """
        pass

    def tearDown(self):
        """ add here functions to call after passing the test
        """
        pass

    def test_001(self):
        """test the help command

        """
        res = os.popen('python openstriato.py -h').read()
        assert res == "openstriato.py -c <config> -do <doaction> -add <addaction>\n"

    def test_002(self):
        """test the add command

        """
        pass
