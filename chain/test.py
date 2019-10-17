from chain import ChainLink
import sys
from Selector import Selector
from chain_map import ChainMap
import getopt

opts, args = getopt.getopt(sys.argv[1:], "i:m:")
opts = dict(opts)
my_index = opts.get("-i")
if my_index is not None:
    my_index = int(my_index)
map_file = opts["-m"]

map = ChainMap(map_file)
sel = Selector()

class CallBack(object):

    def messageConfirmed(self, msg):
        print("Message confirmed: %s" % (msg,))
        
    def messageReceived(self, msg):
        print("Message received: %s" % (msg,))


cs = ChainLink(my_index, map.chainMap(), CallBack(), sel)

cs.broadcast("Hello all", need_confirmation=True)


while True:
    print ("call run()...")
    cs.run(10)
