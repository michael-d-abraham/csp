# csp
assignment 3 


# CS4300-CSP v1 — Tiny CSP Format + Starter Code

This bundle gives students a tiny, readable CSP problem format and a ready-to-use parser and solver so they can focus on **modeling** and **search**.

## Contents
- `cs4300_csp.py` — Data model + constraint helpers + a plain backtracking solver (with forward checking).
- `cs4300_csp_parser.py` — Parser for the **CS4300-CSP v1** text format.
- `run_csp.py` — Small CLI driver to parse and solve a `.csp` file.
- `examples/` — A few sample problems in the new format:
  - `futoshiki4x4.csp`
  - `tiny_schedule.csp`
  - `send_more_money.csp`

## CS4300-CSP v1 (format)
- Line-oriented, `#` starts a comment.
- Sections: `VARS:` then `CONS:`
- Domains: `[1,2,3]` or `range(1,4)` (inclusive)
- Constraints supported:
  - `alldiff(v1,v2,...)`
  - Binary: `eq(x,y)`, `neq(x,y)`, `lt(x,y)`, `le(x,y)`, `gt(x,y)`, `ge(x,y)`
  - Membership: `in(x,[values])`
  - Sum: `sum([x1,x2,...]) op K` where `op` in `== != <= < >= >`
  - Table: `table([x1,x2,...]) allowed [[t11,t12,...],[...]]`

## Quick start
```bash
# (Optional) create a venv
python -m venv .venv && source .venv/bin/activate

# Solve an example
python run_csp.py examples/futoshiki4x4.csp

# Try another
python run_csp.py examples/tiny_schedule.csp
python run_csp.py examples/send_more_money.csp
```

## Assignment ideas
Students can:
1) Write a problem spec in ⟨X,D,C⟩ **and** in CS4300-CSP v1.
2) Implement or extend the solver (e.g., MRV/LCV/AC-3).
3) Provide multiple `.csp` instances and report runtime/branching behavior.
