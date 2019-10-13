#!/bin/sh -f
#
# @(#) $Id: fipc_startup.sh,v 1.2 1999/10/13 16:46:14 ivm Exp $
#
# $Author: ivm $
#
# This is non-FUE version of fipc_startup.sh
#
# $Log: fipc_startup.sh,v $
# Revision 1.2  1999/10/13 16:46:14  ivm
# Added instructions
#
# Revision 1.1  1999/10/13 16:00:38  ivm
# Added non-FUE scripts
#
#
#

# Edit the following 2 lines to reflect your configuration

fipc_user=FIPC_USER			# any non-privileged user will do
. FIPC_ROOT/bin/setup_fipc.sh

if [ ! -r "$FIPC_MAP_FILE" ]; then
	exit 0
fi
 
lst=`cat $FIPC_MAP_FILE | cut -d" " -f1 `
myh=`hostname | cut -f1 -d"."`
for h in $lst ;do
	if [ "$h" = "$myh" ] ;then
		su $fipc_user -c "$FIPC_DIR/bin/run.sh $FIPC_DIR/bin/fipc-srv.sh >/dev/null </dev/null 2>/dev/null &"
	fi
done
#
# start local
#

$FIPC_DIR/bin/run.sh $FIPC_DIR/bin/run_local.sh >/dev/null </dev/null 2>/dev/null &

