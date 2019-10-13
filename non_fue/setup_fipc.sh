#!/bin/sh -f
#
# @(#) $Id: setup_fipc.sh,v 1.2 1999/10/13 16:46:15 ivm Exp $
#
# $Author: ivm $
#
# This script should be sourced by a non-FUE user to set up necessary
# environment variables to use FIPC
#
# $Log: setup_fipc.sh,v $
# Revision 1.2  1999/10/13 16:46:15  ivm
# Added instructions
#
# Revision 1.1  1999/10/13 16:00:39  ivm
# Added non-FUE scripts
#
#

# Edit the following 2 lines to reflect your configuration

fipc_dir=FIPC_ROOT
fipc_config=FIPC_CONFIG_DIR


FIPC_ROOT=$fipc_dir
FIPC_DIR=$fipc_dir
FIPC_MAP_FILE=$fipc_config/fipc.cfg

if [ ! -r ${FIPC_MAP_FILE} ]; then
	echo Can not find FIPC configuration file at $FIPC_MAP_FILE
	exit 1
fi

if [ ! -d ${FIPC_DIR} ]; then
	echo FIPC root directory not found at $FIPC_DIR
	exit 1
fi

if [ -z "$PYTHONPATH" ]; then
	PYTHONPATH=${FIPC_DIR}/lib:${FIPC_DIR}/bin
else
	PYTHONPATH=${FIPC_DIR}/lib:${FIPC_DIR}/bin:${PYTHONPATH}
fi

if [ -z "$PATH" ]; then
	PATH=${FIPC_DIR}/bin:${FIPC_DIR}/lib
else
	PATH=${FIPC_DIR}/bin:${FIPC_DIR}/lib:${PATH}
fi

export FIPC_ROOT FIPC_DIR FIPC_MAP_FILE PYTHONPATH PATH



