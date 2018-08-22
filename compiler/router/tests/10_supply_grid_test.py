#!/usr/bin/env python3
"Run a regresion test the library cells for DRC"

import unittest
from testutils import header,openram_test
import sys,os
sys.path.append(os.path.join(sys.path[0],"../.."))
sys.path.append(os.path.join(sys.path[0],".."))
import globals
import debug

OPTS = globals.OPTS

class no_blockages_test(openram_test):
    """
    Simplest two pin route test with no blockages.
    """

    def runTest(self):
        globals.init_openram("config_{0}".format(OPTS.tech_name))
        from gds_cell import gds_cell
        from design import design
        from supply_router import supply_router as router

        class routing(design, openram_test):
            """
            A generic GDS design that we can route on.
            """
            def __init__(self, name):
                design.__init__(self, "top")

                # Instantiate a GDS cell with the design
                gds_file = "{0}/{1}.gds".format(os.path.dirname(os.path.realpath(__file__)),name)
                cell = gds_cell(name, gds_file)
                self.add_inst(name=name,
                              mod=cell,
                              offset=[0,0])
                self.connect_inst([])
                
                r=router(gds_file)
                layer_stack =("metal3","via1","metal2")
                self.assertTrue(r.route(self,layer_stack))

        r=routing("10_supply_grid_test_{0}".format(OPTS.tech_name))
        self.local_drc_check(r)
        
        # fails if there are any DRC errors on any cells
        globals.end_openram()

# instantiate a copy of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
