#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#
import unittest
from testutils import *
import sys,os
sys.path.append(os.getenv("OPENRAM_HOME"))
import globals
from globals import OPTS
from sram_factory import factory
import debug

class single_bank_wmask_test(openram_test):

    def runTest(self):
        globals.init_openram("config_{0}".format(OPTS.tech_name))
        from sram_config import sram_config


        c = sram_config(word_size=8,
                        write_size=4,
                        num_words=16,
                        num_banks=1)

        c.words_per_row=1
        factory.reset()
        c.recompute_sizes()
        debug.info(1, "No column mux")
        a = factory.create("bank", sram_config=c)
        self.local_check(a)

        c.num_words=32
        c.words_per_row=2
        factory.reset()
        c.recompute_sizes()
        debug.info(1, "Two way column mux")
        a = factory.create("bank", sram_config=c)
        self.local_check(a)

        c.num_words=64
        c.words_per_row=4
        factory.reset()
        c.recompute_sizes()
        debug.info(1, "Four way column mux")
        a = factory.create("bank", sram_config=c)
        self.local_check(a)

        c.num_words=128
        c.words_per_row=8
        factory.reset()
        c.recompute_sizes()
        debug.info(1, "Eight way column mux")
        a = factory.create("bank", sram_config=c)
        self.local_check(a)
        
        globals.end_openram()
        
# run the test from the command line
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main(testRunner=debugTestRunner())