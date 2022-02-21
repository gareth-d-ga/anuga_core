
"""Test a run of the sequential shallow water domain against
a run of the parallel shallow water domain.

WARNING: This assumes that the command to run jobs is mpiexec.
Tested with MPICH and LAM (Ole)
"""

# ------------------------
# Import necessary modules
# ------------------------
import platform
import unittest
import numpy as num
import os
import subprocess

verbose = False


class Test_parallel_shallow_domain(unittest.TestCase):
    def setUp(self):
        # Run the sequential and parallel simulations to produce sww files for comparison.

        path = os.path.dirname(__file__)  # Get folder where this script lives
        run_filename = os.path.join(path, 'run_parallel_shallow_domain.py')

        # ----------------------
        # First run sequentially
        # ----------------------
        cmd = 'python ' + run_filename
        if verbose:
            print(cmd)

        result = subprocess.run(cmd.split(), capture_output=True)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise Exception(result.stderr)

        # --------------------
        # Then run in parallel
        # --------------------
        if platform.system() == 'Windows':
            extra_options = ' '
        else:
            # E.g. for Ubuntu Linux
            extra_options = '--oversubscribe'

        cmd = 'mpiexec -np 3 ' + extra_options + ' python ' + run_filename
        if verbose:
            print(cmd)

        result = subprocess.run(cmd.split(), capture_output=True)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise Exception(result.stderr)

    def tearDown(self):
        os.remove('shallow_water_sequential.sww')
        os.remove('shallow_water_parallel.sww')

    def test_parallel_sw_flow(self):
        # Note if this is imported at the top level
        # it'll interfere with running the subprocesses.
        import anuga.utilities.plot_utils as util

        # Assuming both sequential and parallel simulations have been run, compare the
        # merged sww files from the parallel run to the sequential output.
        if verbose:
            print('Comparing SWW files')

        sdomain_v = util.get_output('shallow_water_sequential.sww')
        sdomain_c = util.get_centroids(sdomain_v)

        pdomain_v = util.get_output('shallow_water_parallel.sww')
        pdomain_c = util.get_centroids(pdomain_v)

        # Compare values from the two sww files
        if verbose:
            order = 0
            print('Centroid values')
            print(num.linalg.norm(sdomain_c.x - pdomain_c.x, ord=order))
            print(num.linalg.norm(sdomain_c.y - pdomain_c.y, ord=order))
            print(num.linalg.norm(sdomain_c.stage[-1] - pdomain_c.stage[-1], ord=order))
            print(num.linalg.norm(sdomain_c.xmom[-1] - pdomain_c.xmom[-1], ord=order))
            print(num.linalg.norm(sdomain_c.ymom[-1] - pdomain_c.ymom[-1], ord=order))
            print(num.linalg.norm(sdomain_c.xvel[-1] - pdomain_c.xvel[-1], ord=order))
            print(num.linalg.norm(sdomain_c.yvel[-1] - pdomain_c.yvel[-1], ord=order))

        msg = 'Values not identical'
        assert num.allclose(sdomain_c.stage, pdomain_c.stage), msg
        assert num.allclose(sdomain_c.xmom, pdomain_c.xmom)
        assert num.allclose(sdomain_c.ymom, pdomain_c.ymom)
        assert num.allclose(sdomain_c.xvel, pdomain_c.xvel)
        assert num.allclose(sdomain_c.yvel, pdomain_c.yvel)

        assert num.allclose(sdomain_v.x, pdomain_v.x)
        assert num.allclose(sdomain_v.y, pdomain_v.y)


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = unittest.makeSuite(Test_parallel_shallow_domain, 'test')
    runner.run(suite)
