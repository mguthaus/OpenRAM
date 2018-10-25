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

#@unittest.skip("SKIPPING 22_psram_func_test")
class psram_func_test(openram_test):

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
        if not OPTS.spice_exe:
            debug.error("Could not find {} simulator.".format(OPTS.spice_name),-1)

        from sram import sram
        from sram_config import sram_config
        c = sram_config(word_size=4,
                        num_words=32,
                        num_banks=1)
        c.words_per_row=1
        
        OPTS.num_rw_ports = 1
        OPTS.num_w_ports = 1
        OPTS.num_r_ports = 1
        
        # no column mux
        debug.info(1, "Functional test for multi-port ({0}RW {1}W {2}R) sram with {3}bit words, {4}words, {5}words per row, {6}banks".format(OPTS.num_rw_ports,
                                                                                                                                             OPTS.num_w_ports,
                                                                                                                                             OPTS.num_r_ports,
                                                                                                                                             c.word_size,
                                                                                                                                             c.num_words,
                                                                                                                                             c.words_per_row,
                                                                                                                                             c.num_banks))
        s = sram(c, name="sram1")
        tempspice = OPTS.openram_temp + "temp.sp"
        s.sp_write(tempspice)
        corner = (OPTS.process_corners[0], OPTS.supply_voltages[0], OPTS.temperatures[0])
        
        f = functional(s.s, tempspice, corner)
        f.num_cycles = 10
        (fail,error) = f.run()
        self.assertTrue(fail,error)
        self.reset()
        
        # 2-way column mux
        c.num_words = 64
        c.words_per_row = 2
        debug.info(1, "Functional test for multi-port ({0}RW {1}W {2}R) sram with {3}bit words, {4}words, {5}words per row, {6}banks".format(OPTS.num_rw_ports,
                                                                                                                                             OPTS.num_w_ports,
                                                                                                                                             OPTS.num_r_ports,
                                                                                                                                             c.word_size,
                                                                                                                                             c.num_words,
                                                                                                                                             c.words_per_row,
                                                                                                                                             c.num_banks))
        s = sram(c, name="sram2")
        s.sp_write(tempspice)

        f = functional(s.s, tempspice, corner)
        f.num_cycles = 10
        (fail,error) = f.run()
        self.assertTrue(fail,error)
        self.reset()
        """ 
        # 4-way column mux
        c.num_words = 256
        c.words_per_row = 4
        debug.info(1, "Functional test for multi-port ({0}RW {1}W {2}R) sram with {3}bit words, {4}words, {5}words per row, {6}banks".format(OPTS.num_rw_ports,
                                                                                                                                             OPTS.num_w_ports,
                                                                                                                                             OPTS.num_r_ports,
                                                                                                                                             c.word_size,
                                                                                                                                             c.num_words,
                                                                                                                                             c.words_per_row,
                                                                                                                                             c.num_banks))
        s = sram(c, name="sram1")
        s.sp_write(tempspice)

        f = functional(s.s, tempspice, corner)
        f.num_cycles = 10
        (fail,error) = f.run()
        self.assertTrue(fail,error)
        self.reset()
        
        # 8-way column mux
        c.num_words = 512
        c.words_per_row = 8
        debug.info(1, "Functional test for multi-port ({0}RW {1}W {2}R) sram with {3}bit words, {4}words, {5}words per row, {6}banks".format(OPTS.num_rw_ports,
                                                                                                                                             OPTS.num_w_ports,
                                                                                                                                             OPTS.num_r_ports,
                                                                                                                                             c.word_size,
                                                                                                                                             c.num_words,
                                                                                                                                             c.words_per_row,
                                                                                                                                             c.num_banks))
        s = sram(c, name="sram1")
        s.sp_write(tempspice)

        f = functional(s.s, tempspice, corner)
        f.num_cycles = 10
        (fail,error) = f.run()
        self.assertTrue(fail,error)
        self.reset()
        """
        globals.end_openram()
        
# instantiate a copdsay of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()