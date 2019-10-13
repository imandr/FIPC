#!/bin/sh
#
# @(#) $Id: run.sh,v 1.1 1999/10/13 16:00:39 ivm Exp $
#
# $Author: ivm $
#
# $Log: run.sh,v $
# Revision 1.1  1999/10/13 16:00:39  ivm
# Added non-FUE scripts
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

