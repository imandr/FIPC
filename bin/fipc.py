#
# @(#) $Id: fipc.py,v 1.2 1999/10/04 15:47:28 ivm Exp $
#
# $Author: ivm $
#
# $Log: fipc.py,v $
# Revision 1.2  1999/10/04 15:47:28  ivm
# Fixed bugs
#
# Revision 1.1  1999/07/12 19:35:53  ivm
# *** empty log message ***
#
# Revision 1.1  1999/05/24 16:37:51  ivm
# Initial revision
#
#

import fipc_ui_api
import sys

if __name__ == '__main__':		
	sys.exit(fipc_ui_api.main(sys.argv))
	
