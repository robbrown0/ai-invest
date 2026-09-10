#!/usr/local/bin/python3 -I
"""No-argument protected execution entry; never accepts credentials as arguments."""
from pathlib import Path
import sys
if len(sys.argv)!=1: raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'execution')]
from ai_invest_execution.paper_bootstrap import main
raise SystemExit(main())
