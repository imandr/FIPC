#!/bin/sh -f
#
# @(#) $Id: fipc-srv.sh,v 1.2 1999/08/17 21:55:55 ivm Exp $
#
# $Author: ivm $
# 
# $Log: fipc-srv.sh,v $
# Revision 1.2  1999/08/17 21:55:55  ivm
# Made UPS compliant
# Use single config file
#
# Revision 1.1  1999/07/12 19:35:53  ivm
# *** empty log message ***
#
# Revision 1.10  1999/07/12 19:22:38  ivm
# *** empty log message ***
#
# Revision 1.9  1999/05/21 19:49:43  ivm
# Fixed PYTHONPATH
#
# Revision 1.8  1999/05/21  19:31:18  ivm
# Include OS-specific dirs into PYTHONPATH
#
# Revision 1.7  1999/05/21  14:22:36  ivm
# Latest version with mixed ChainLink
#
# Revision 1.6  1999/05/20  19:18:33  ivm
# Imperfect working version, with request suspension
#
# Revision 1.6  1999/05/20  19:18:33  ivm
# Imperfect working version, with request suspension
#
# Revision 1.5  1999/05/18  15:02:22  ivm
# *** empty log message ***
#
# Revision 1.5  1999/05/18  15:02:22  ivm
# *** empty log message ***
#
# Revision 1.4  1999/05/17  15:10:20  ivm
# *** empty log message ***
#
# Revision 1.3  1999/05/14  20:10:59  ivm
# *** empty log message ***
#
# Revision 1.3  1999/05/14  20:10:59  ivm
# *** empty log message ***
#
# Revision 1.1  1999/05/12  21:18:23  ivm
# Initial revision
#
#

#+FUE
#
# assuming that python, FIPC_DIR, FIPC_ROOT, PYTHONPATH are set up

python $FIPC_DIR/bin/fipc-srv.py -m $FIPC_ROOT/fipc.cfg $@
