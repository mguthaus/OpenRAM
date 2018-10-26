#!/usr/bin/env python3
"""
Run a regression test on various srams
"""

import unittest
from testutils import header,openram_test
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
from globals import OPTS
import debug

@unittest.skip("SKIPPING 22_psram_1bank_8mux_func_test")
class psram_1bank_8mux_func_test(openram_test):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        OPTS.analytical_delay = False
        OPTS.netlist_only = True
        OPTS.bitcell = "pbitcell"
        OPTS.replica_bitcell="replica_pbitcell"
        
        # This is a hack to reload the characterizer __init__ with the spice version
        from importlib import reload
        import characterizer
        reload(characterizer)
        from characterizer import functional
        from sram import sram
        from sram_config import sram_config
        c = sram_config(word_size=4,
                        num_words=512,
                        num_banks=1)
        c.words_per_row=8
        debug.info(1, "Functional test for psram with {} bit words, {} words, {} words per row, {} banks".format(c.word_size,
                                                                                                                c.num_words,
                                                                                                                c.words_per_row,
                                                                                                                c.num_banks))
        s = sram(c, name="sram")
        s.sp_write(tempspice)
        
        corner = (OPTS.process_corners[0], OPTS.supply_voltages[0], OPTS.temperatures[0])
        
        f = functional(s.s, tempspice, corner)
        f.num_cycles = 10
        (fail, error) = f.run()
        self.assertTrue(fail,error)
        
        globals.end_openram()
        
# instantiate a copy of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()