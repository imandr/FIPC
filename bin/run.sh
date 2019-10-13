#!/bin/sh
#
# @(#) $Id: run.sh,v 1.1 1999/07/12 19:35:54 ivm Exp $
#
# $Author: ivm $
#
# $Log: run.sh,v $
# Revision 1.1  1999/07/12 19:35:54  ivm
# *** empty log message ***
#
# Revision 1.6  1999/06/14 20:28:53  ivm
# *** empty log message ***
#
# Revision 1.5  1999/05/21  19:31:18  ivm
# Include OS-specific dirs into PYTHONPATH
#
# Revision 1.5  1999/05/21  19:31:18  ivm
# Include OS-specific dirs into PYTHONPATH
#
# Revision 1.4  1999/05/20  20:36:05  ivm
# Fixed recursive call
#
# Revision 1.4  1999/05/20  20:36:05  ivm
# Fixed recursive call
#
# Revision 1.3  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.3  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.2  1999/05/17  18:05:32  ivm
# Just added RCS headers
#
#

if [ -x $1 ] ;then
	while true ;do
		$@
		sleep 20
	done
else
	echo "run.sh: can not find $1"
	echo "run.sh: exiting"
fi

