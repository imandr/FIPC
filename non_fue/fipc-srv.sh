#!/bin/sh -f
#
# @(#) $Id: fipc-srv.sh,v 1.2 1999/10/13 16:46:14 ivm Exp $
#
# $Author: ivm $
# 
# $Log: fipc-srv.sh,v $
# Revision 1.2  1999/10/13 16:46:14  ivm
# Added instructions
#
# Revision 1.1  1999/10/13 16:00:38  ivm
# Added non-FUE scripts
#
#

# Edit the following line to reflect your configuration

. FIPC_ROOT/bin/setup_fipc.sh

python $FIPC_DIR/bin/fipc-srv.py -m $FIPC_MAP_FILE $@
