#!/bin/sh -f
#
# @(#) $Id: fipc_startup.sh,v 1.1 1999/09/14 16:21:28 ivm Exp $
#
# $Author: ivm $
#
# $Log: fipc_startup.sh,v $
# Revision 1.1  1999/09/14 16:21:28  ivm
# Added fipc_startup.sh
#
#

. /fnal/ups/etc/setups.sh
setup fipc

if [ -z "$SETUP_FIPC" -o -z "$FIPC_DIR" -o -z "$FIPC_ROOT" ]; then
	exit 0
fi

if [ ! -r "$FIPC_ROOT/fipc.cfg" ]; then
	exit 0
fi
 
lst=`cat $FIPC_ROOT/fipc.cfg | cut -d" " -f1 `
myh=`hostname | cut -f1 -d"."`
for h in $lst ;do
	if [ "$h" = "$myh" ] ;then
		su farms -c "$FIPC_DIR/bin/run.sh $FIPC_DIR/bin/fipc-srv.sh >/dev/null </dev/null 2>/dev/null &"
	fi
done
#
# start local
#

$FIPC_DIR/bin/run.sh $FIPC_DIR/bin/run_local.sh >/dev/null </dev/null 2>/dev/null &

