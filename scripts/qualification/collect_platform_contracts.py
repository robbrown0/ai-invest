#!/usr/bin/env python3
"""Read-only, bounded platform contract collector; never prints secrets or raw host data."""
import json, os, platform, re, shutil, subprocess, sys
from pathlib import Path

MAX=8192

def run(args, timeout=3):
    try:
        r=subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False, close_fds=True,
                         env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin", "LANG":"C", "LC_ALL":"C"})
        return {"returncode": r.returncode, "stdout_len": len(r.stdout), "stderr_len": len(r.stderr), "stdout": r.stdout[:MAX]}
    except Exception:
        return {"returncode": None, "stdout_len": 0, "stderr_len": 0, "stdout": ""}

def version(args):
    r=run(args)
    first=r["stdout"].splitlines()[0] if r["stdout"].splitlines() else ""
    m=re.search(r"([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:p[0-9]+)?)", first)
    return {"returncode":r["returncode"], "version_present":bool(m), "version_length":len(m.group(1)) if m else 0}

def session_summary():
    r=run(["/usr/bin/loginctl","--no-pager","--no-ask-password","show-session","self",
           "--property=Active","--property=Remote","--property=Type","--property=Class",
           "--property=User","--property=State","--property=TTY","--property=Service"])
    keys={}; malformed=0
    for line in r["stdout"].splitlines():
        if "=" not in line: malformed+=1; continue
        k,v=line.split("=",1)
        if k in {"Active","Remote","Type","Class","User","State","TTY","Service"}:
            keys[k]={"present":True,"length":len(v),"is_yes":v=="yes","is_no":v=="no","is_numeric":v.isdigit()}
    return {"api_returncode":r["returncode"],"stdout_len":r["stdout_len"],"malformed_lines":malformed,"fields":keys}

def list_summary():
    r=run(["/usr/bin/loginctl","--no-pager","--no-ask-password","list-sessions","--no-legend"])
    rows=[]; nonrecords=0; malformed_numeric=0
    for line in r["stdout"].splitlines():
        f=line.split()
        if not f: continue
        if not re.fullmatch(r"[0-9]+",f[0]): nonrecords+=1; continue
        rows.append(len(f))
        if not (1<=len(f)<=16): malformed_numeric+=1
    return {"api_returncode":r["returncode"],"stdout_len":r["stdout_len"],"numeric_row_count":len(rows),"numeric_field_counts":sorted(set(rows)),"nonrecord_row_count":nonrecords,"malformed_numeric_rows":malformed_numeric}

def tty_summary():
    result={"fds_are_tty":[],"tty_names_are_pts":[],"same_tty_name":False,"ssh_tty_present":bool(os.environ.get("SSH_TTY")),"ssh_connection_shape":None}
    names=[]
    for fd in (0,1,2):
        try:
            name=os.ttyname(fd); names.append(name)
            result["fds_are_tty"].append(bool(os.isatty(fd))); result["tty_names_are_pts"].append(name.startswith("/dev/pts/"))
        except Exception:
            result["fds_are_tty"].append(False); result["tty_names_are_pts"].append(False)
    result["same_tty_name"]=bool(names) and len(set(names))==1
    c=os.environ.get("SSH_CONNECTION")
    result["ssh_connection_shape"] = None if c is None else {"field_count":len(c.split()),"field_lengths":[len(x) for x in c.split()]}
    return result

def main():
    fixed=("DISPLAY","WAYLAND_DISPLAY","TMUX","STY","SSH_ORIGINAL_COMMAND","LD_PRELOAD","LD_LIBRARY_PATH","PYTHONPATH","PYTHONHOME")
    out={"collector":"ai-invest-platform-contracts-v1","secret_entry_authorized":False,
         "host":{"platform":platform.system(),"kernel_release_length":len(platform.release()),"python":platform.python_version()},
         "commands":{"sudo":version(["/usr/bin/sudo","-V"]),"systemd":version(["/usr/bin/systemd","--version"]),"loginctl":version(["/usr/bin/loginctl","--version"]),"ssh_client":version(["/usr/bin/ssh","-V"])},
         "tty":tty_summary(),"environment_markers":{k:bool(os.environ.get(k)) for k in fixed},
         "logind_self":session_summary(),"logind_list":list_summary()}
    print(json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__": main()
