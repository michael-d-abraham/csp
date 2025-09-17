from __future__ import annotations
import re, ast
from typing import Dict, List, Tuple
from cs4300_csp import CSP, c_alldiff, c_bin, c_in, c_sum, c_table, c_add10

BINOPS = {
    "eq":  ("==", lambda x,y: x == y),
    "neq": ("!=", lambda x,y: x !=  y),
    "lt":  ("<",  lambda x,y: x <   y),
    "le":  ("<=", lambda x,y: x <=  y),
    "gt":  (">",  lambda x,y: x >   y),
    "ge":  (">=", lambda x,y: x >=  y),
}

def _clean(lines: List[str]) -> List[str]:
    out = []
    for ln in lines:
        # preserve blank lines during table capture; strip comments elsewhere
        if "#" in ln:
            ln = ln.split("#",1)[0]
        ln = ln.rstrip("\n")
        if not ln.strip():
            out.append("")  # keep empties so table capture can span
        else:
            out.append(ln.strip())
    # drop leading/trailing empties
    while out and out[0] == "": out.pop(0)
    while out and out[-1] == "": out.pop()
    return out

def _parse_domain(tok: str) -> List[int]:
    tok = tok.strip()
    if tok.startswith("range(") and tok.endswith(")"):
        a,b = tok[6:-1].split(","); a=int(a); b=int(b)
        return list(range(a, b+1))
    if tok.startswith("[") and tok.endswith("]"):
        xs = ast.literal_eval(tok)
        return list(map(int, xs))
    raise ValueError(f"Bad domain: {tok}")

def _parse_varlist(s: str) -> List[str]:
    return [t.strip() for t in s.split(",") if t.strip()]

def parse_cs4300(path: str) -> CSP:
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    lines = _clean(raw_lines)

    try:
        vi = lines.index("VARS:")
        ci = lines.index("CONS:")
    except ValueError:
        raise ValueError("File must contain 'VARS:' and 'CONS:' headings.")

    varlines = [ln for ln in lines[vi+1:ci] if ln.strip()]
    conslines = lines[ci+1:]

    # variables
    domains: Dict[str, List[int]] = {}
    var_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$")
    for ln in varlines:
        m = var_re.match(ln)
        if not m:
            raise ValueError(f"Bad variable line: {ln}")
        name, dom = m.group(1), m.group(2)
        domains[name] = _parse_domain(dom)

    # constraints (supports multiline table blocks)
    constraints = []
    i = 0
    while i < len(conslines):
        ln = conslines[i].strip()
        i += 1
        if not ln:
            continue

        # alldiff
        if ln.startswith("alldiff(") and ln.endswith(")"):
            vars = _parse_varlist(ln[len("alldiff("):-1])
            constraints.append(c_alldiff(vars))
            continue

        # binary eq/neq/lt/le/gt/ge
        matched = False
        for key,(sym,op) in BINOPS.items():
            if ln.startswith(f"{key}(") and ln.endswith(")"):
                body = ln[len(key)+1:-1]
                x,y = [t.strip() for t in body.split(",")]
                constraints.append(c_bin(op, x, y, key))
                matched = True
                break
        if matched:
            continue

        # in(x,[...])
        if ln.startswith("in(") and ln.endswith(")"):
            body = ln[len("in("):-1]
            x, lst = body.split(",",1)
            allowed = ast.literal_eval(lst.strip())
            constraints.append(c_in(x.strip(), list(map(int, allowed))))
            continue

        # sum([vars]) op K
        m = re.match(r"sum\(\[(.+)\]\)\s*(==|!=|<=|<|>=|>)\s*(-?\d+)$", ln)
        if m:
            vlist = _parse_varlist(m.group(1))
            opstr = m.group(2)
            k = int(m.group(3))
            constraints.append(c_sum(vlist, opstr, k))
            continue


        # add10(X,Y,Cin -> Z,Cout)
        m = re.match(r"add10\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*->\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)$", ln)
        if m:
            x, y, cin, z, cout = m.groups()
            constraints.append(c_add10(x, y, cin, z, cout))
            continue

                # table([vars]) allowed [ ... ]  (possibly spanning multiple lines)
        if ln.startswith("table(") and "allowed" in ln:
            # capture var list
            m = re.match(r"table\(\[(.+)\]\)\s*allowed\s*(\[.*)$", ln)
            if not m:
                raise ValueError(f"Bad table constraint header: {ln}")
            vlist = _parse_varlist(m.group(1))
            tail = m.group(2)

            buf = tail
            # if tail doesn't end with ']', keep concatenating lines until it does
            while not buf.strip().endswith("]"):
                if i >= len(conslines):
                    raise ValueError("Unterminated table allowed list")
                buf += " " + conslines[i].strip()
                i += 1

            tuples = ast.literal_eval(buf)
            constraints.append(c_table(vlist, [tuple(map(int,t)) for t in tuples]))
            continue

        raise ValueError(f"Unknown constraint: {ln}")

    return CSP(domains=domains, constraints=constraints)
