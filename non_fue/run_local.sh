#!/bin/sh -f
#
# @(#) $Id: run_local.sh,v 1.2 1999/10/13 16:46:14 ivm Exp $
#
# $Author: ivm $
#
# $Log: run_local.sh,v $
# Revision 1.2  1999/10/13 16:46:14  ivm
# Added instructions
#
# Revision 1.1  1999/10/13 16:00:39  ivm
# Added non-FUE scripts
#
#

# Edit the following line to reflect your configuration

. FIPC_ROOT/bin/setup_fipc.sh

python $FIPC_DIR/bin/fipc_local.py

