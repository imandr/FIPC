#
# @(#) $Id: fipc_map.py,v 1.2 2001/09/28 17:06:17 ivm Exp $
#
# $Author: ivm $
#
#       FIPCMap class
#       =============
#       FIPCMap class implements parsing of FIPC configuration file.
#       File format is:
#       -----------------------------------------------------------------
#       host chain-port server-port #comments
#       host chain-port server-port #comments
#       host chain-port server-port #comments
#       .....
#       -----------------------------------------------------------------
#       
#

# $Log: fipc_map.py,v $
# Revision 1.2  2001/09/28 17:06:17  ivm
# Made it work with Python 2.1
#
# Revision 1.1  1999/08/17 22:01:59  ivm
# Added fipc_map.py
#
#

"""
Chain map file:

map:
   - ["host", chain_port, server_port]
   - ["host", chain_port, server_port]
   ...
"""


import yaml

class   ChainMap:
    def __init__(self, file_or_name):
        self.CMap = []
        self.SMap = []
        f = file_or_name
        if type(f) == type(''):
            f = open(f)
        map = yaml.load(f.read(), Loader=yaml.SafeLoader)["map"]
        self.CMap = [(h, cp) for h, cp, sp in map]
        self.SMap = [(h, sp) for h, cp, sp in map]

    def chainMap(self):
        return self.CMap
        
    def serverMap(self):
        return self.SMap
                        
if __name__ == '__main__':
        import sys
        if len(sys.argv) < 2:
                print('Usage: fipc-map.py fipc.cfg')
        else:
                f = FIPCMap(sys.argv[1])
                print('Chain map:')
                for a in f.chainMap():
                        h, p = a
                        print((h, p))
                print('')
                print('Server map:')
                for a in f.serverMap():
                        h, p = a
                        print((h, p))
                
