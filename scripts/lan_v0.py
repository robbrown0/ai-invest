#!/usr/local/bin/python3 -I
import sys
if len(sys.argv)!=1: raise SystemExit(1)
sys.path.insert(0,'/opt/ai-invest/backend')
from ai_invest_core.lan_app import main
raise SystemExit(main())
