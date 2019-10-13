#!/bin/csh -f
#
# @(#) $Id: setup_fipc.csh,v 1.2 1999/10/13 16:46:15 ivm Exp $
#
# $Author: ivm $
#
# This script should be sourced by a non-FUE user to set up necessary
# environment variables to use FIPC
#
# $Log: setup_fipc.csh,v $
# Revision 1.2  1999/10/13 16:46:15  ivm
# Added instructions
#
# Revision 1.1  1999/10/13 16:00:39  ivm
# Added non-FUE scripts
#
#

# Edit the following 2 lines to reflect your configuration

set fipc_dir = FIPC_ROOT
set fipc_config = FIPC_CONFIG_DIR

if ( ! -r ${fipc_config}/fipc.cfg ) then
	echo Can not find FIPC configuration file at ${fipc_config}/fipc.cfg
	exit 1
endif

if ( ! -d $fipc_dir ) then
	echo FIPC root directory not found at ${fipc_dir}
	exit 1
endif

if ( $?PYTHONPATH ) then
	setenv PYTHONPATH ${FIPC_DIR}/lib:${FIPC_DIR}/bin:${PYTHONPATH}
else
	setenv PYTHONPATH ${FIPC_DIR}/lib:${FIPC_DIR}/bin
endif

if ( $?PATH ) then
	setenv PATH ${FIPC_DIR}/bin:${FIPC_DIR}/lib:${PATH}
else
	setenv PATH ${FIPC_DIR}/bin:${FIPC_DIR}/lib
endif

