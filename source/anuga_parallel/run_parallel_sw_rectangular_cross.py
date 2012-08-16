#########################################################
#
#  Main file for parallel mesh testing.
#
#  This is a modification of the run_parallel_advection.py
# file.
#
#
#  Authors: Linda Stals, Steve Roberts and Matthew Hardy,
# June 2005
#
#
#
#########################################################

import time
import sys

import numpy as num

from print_stats import print_test_stats, build_full_flag

#----------------------------
# Sequential interface
#---------------------------
from anuga import Domain
from anuga import Transmissive_boundary, Reflective_boundary
from anuga import rectangular_cross_domain

#----------------------------
# Parallel interface
#---------------------------
from anuga_parallel import distribute, myid, numprocs, finalize, barrier

#from anuga_parallel import Parallel_shallow_water_domain
#from anuga_parallel import parallel_rectangle


verbose = True

#--------------------------------------------------------------------------
# Setup Domain only on processor 0
#--------------------------------------------------------------------------
if myid == 0:
    length = 2.0
    width = 2.0
    dx = dy = 0.02
    domain = rectangular_cross_domain(int(length/dx), int(width/dy),
                                              len1=length, len2=width)

    domain.set_store(False)
    domain.set_quantity('elevation', -1.0)
    domain.set_quantity('stage', 1.0)
else:
    domain = None



if myid == 0 and verbose: print 'DISTRIBUTING DOMAIN'
domain = distribute(domain,verbose=verbose)

print 'after parallel domain'



domain.set_name('sw_rectangle')

#Boundaries
T = Transmissive_boundary(domain)
R = Reflective_boundary(domain)


domain.set_boundary( {'left': R, 'right': R, 'bottom': R, 'top': R, 'ghost': None} )


print 'after set_boundary'



domain.check_integrity()
print 'after check_integrity'

class Set_Stage:
    """Set an initial condition with constant water height, for x<x0
    """

    def __init__(self, x0=0.25, x1=0.75, y0=0.0, y1=1.0, h=5.0, h0=0.0):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.h  = h
        self.h0 = h0

    def __call__(self, x, y):
        return self.h0 + self.h*((x>self.x0)&(x<self.x1)&(y>self.y0)&(y<self.y1))



#domain.set_quantity('stage', Set_Stage(0.2, 0.4, 0.25, 0.75, 1.0, 0.00))


print 'after set quantity'

# Set Evolve parameters
domain.set_flow_algorithm('2_0')




#domain.update_ghosts()


#print 'after evolve parameters'


#import pdb; pdb.set_trace()






yieldstep = 0.05
finaltime = 2.0

barrier()

t0 = time.time()

#Check that the boundary value gets propagated to all elements
for t in domain.evolve(yieldstep = yieldstep, finaltime = finaltime):
    if myid == 0:
        domain.write_time()
        sys.stdout.flush()
						



barrier()

for p in range(numprocs):
    if myid == p:
        print 50*'='
        print 'P%g' %(myid)
        print 'That took %.2f seconds' %(time.time()-t0)
        print 'Communication time %.2f seconds'%domain.communication_time
        print 'Reduction Communication time %.2f seconds'%domain.communication_reduce_time
        print 'Broadcast time %.2f seconds'%domain.communication_broadcast_time
        sys.stdout.flush()

    barrier()


finalize()