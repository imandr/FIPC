#!/bin/sh -f
#
# @(#) $Id: configure.sh,v 1.6 2000/07/27 19:05:37 ivm Exp $
#
# $Author: ivm $
#
# $Log: configure.sh,v $
# Revision 1.6  2000/07/27 19:05:37  ivm
# *** empty log message ***
#
# Revision 1.4  1999/12/10 17:09:26  ivm
# Fixed configure.sh (setup python first)
# Do not enforce '/path/name' in API for now
#
# Revision 1.3  1999/08/18 16:39:53  ivm
# Added fipc_compile.py
#
# Revision 1.2  1999/08/18 16:03:31  ivm
# Fixed some bugs
#
# Revision 1.1  1999/08/17 21:56:41  ivm
# Made UPS compliant
#
#

root=${UPS_OPTIONS}

sed -e s+_ROOT_+${root}+g < ${UPS_PROD_DIR}/ups/setroot.sh.template \
		> ${UPS_PROD_DIR}/bin/setroot.sh

sed -e s+_ROOT_+${root}+g < ${UPS_PROD_DIR}/ups/setroot.csh.template \
		> ${UPS_PROD_DIR}/bin/setroot.csh

chmod ugo+rx ${UPS_PROD_DIR}/bin/setroot.csh
chmod ugo+rx ${UPS_PROD_DIR}/bin/setroot.sh

. ${SETUPS_DIR}/setups.sh
setup python
setup fcslib

python ${UPS_PROD_DIR}/lib/fipc_compile.py
