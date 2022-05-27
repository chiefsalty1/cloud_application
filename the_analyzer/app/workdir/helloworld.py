from mpi4py import MPI
import socket
import numpy as np

def get_Host_IP(my_rank):
  try:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    print("host: ",host," ipAdd: ", ip, " myrank: ", comm.rank)
  except:
    print("unable to get host and ip")
 

comm = MPI.COMM_WORLD
name = MPI.Get_processor_name()
rank = comm.rank


get_Host_IP(rank)

if rank == 0:
  data = {'key1':[7,2.72,2+3j], 'key2':('abc','xyz')}
else:
  data = None

data = comm.bcast(data, root=0)
print("bcast finished and data on rank %d is: " %comm.rank, data)
