from chain import ChainSegment
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

cs = ChainSegment(my_index, map.chainMap(), sel)

while True:
    cs.run(10)