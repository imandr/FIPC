#!/bin/sh -f
#
# @(#) $Id: run_local.sh,v 1.2 1999/08/17 21:55:56 ivm Exp $
#
# $Author: ivm $
#
# $Log: run_local.sh,v $
# Revision 1.2  1999/08/17 21:55:56  ivm
# Made UPS compliant
# Use single config file
#
# Revision 1.1  1999/07/12 19:35:54  ivm
# *** empty log message ***
#
# Revision 1.7  1999/07/12 19:23:09  ivm
# *** empty log message ***
#
# Revision 1.6  1999/05/21 19:49:43  ivm
# Fixed PYTHONPATH
#
# Revision 1.5  1999/05/21  19:31:18  ivm
# Include OS-specific dirs into PYTHONPATH
#
# Revision 1.4  1999/05/21  14:22:36  ivm
# Latest version with mixed ChainLink
#
# Revision 1.3  1999/05/20  19:18:33  ivm
# Imperfect working version, with request suspension
#
# Revision 1.3  1999/05/20  19:18:33  ivm
# Imperfect working version, with request suspension
#
# Revision 1.2  1999/05/17  18:05:32  ivm
# Just added RCS headers
#
# Revision 1.2  1999/05/17  18:05:32  ivm
# Just added RCS headers
#
#

#+FUE
#
# Assuming python, PYTHONPATH, FIPC_DIR and FIPC_ROOT are set up

python $FIPC_DIR/bin/fipc_local.py

