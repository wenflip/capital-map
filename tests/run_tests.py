"""Test runner for The Capital Map: picks quick or full, runs suites in parallel, prints one line per suite.

Usage:
  python3 run_tests.py <repo> <outdir> [--mode auto|quick|full] [--suite test_x ...] [--workers 4]

Modes (the 80/20 rule):
  quick  the branch's own suites (--suite) plus the SMOKE set, desktop width only, both depths
  full   every suite at all three widths, both depths
  auto   full if the branch touches the engine (ENGINE paths) compared with origin/main, otherwise quick
Ends with a line "DONE <passed>/<total>" so a waiting loop can watch for it.
"""
import argparse, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE / "suites"
SMOKE = ["test_links", "test_hubs", "test_public", "test_flows"]   # structure, hub standard, launch gate, flows
ENGINE = ("assets/", "tools/", "index.html", "_headers", "robots.txt")

ap = argparse.ArgumentParser()
ap.add_argument("repo"); ap.add_argument("outdir")
ap.add_argument("--mode", default="auto", choices=["auto", "quick", "full"])
ap.add_argument("--suite", nargs="*", action="extend", default=[])
ap.add_argument("--workers", type=int, default=4)
a = ap.parse_args()
repo = Path(a.repo).resolve()

def changed_files():
    run = lambda *c: subprocess.run(["git", "-C", str(repo), *c], capture_output=True, text=True).stdout.split()
    return set(run("diff", "--name-only", "origin/main...HEAD")) | set(run("diff", "--name-only")) | set(run("ls-files", "--others", "--exclude-standard"))

mode = a.mode
if mode == "auto":
    engine = sorted(f for f in changed_files() if f.startswith(ENGINE))
    mode = "full" if engine else "quick"
    print(f"auto: {'engine files changed ' + str(engine[:5]) if engine else 'content only'} -> {mode}")

if mode == "full":
    suites = sorted(p.stem for p in TESTS.glob("test_*.py"))
    env_widths = "1366,390,360"
else:
    suites = list(dict.fromkeys([s.removesuffix(".py") for s in a.suite] + SMOKE))
    env_widths = "1366"
missing = [s for s in suites if not (TESTS / f"{s}.py").exists()]
if missing: sys.exit(f"unknown suites: {missing}")
print(f"{mode}: {len(suites)} suites at widths {env_widths}, {a.workers} at a time")

def run(s):
    t0 = time.time()
    env = dict(os.environ, CAPMAP_WIDTHS=env_widths)
    r = subprocess.run([sys.executable, "-I", str(TESTS / f"{s}.py"), str(repo), a.outdir], capture_output=True, text=True, env=env, timeout=1800)
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL ")]
    errs = next((l for l in out.splitlines() if l.startswith("Console errors:")), "Console errors: ?")
    crashed = "Traceback" in out
    ok = not fails and errs.endswith(": 0") and not crashed
    detail = "" if ok else (" | " + "; ".join(sorted(set(fails))[:4]) if fails else "") + (" | CRASHED" if crashed else "")
    return s, ok, f"{'PASS' if ok else 'FAIL'}  {s:<18} {time.time() - t0:5.0f}s  {errs}{detail}"

with ThreadPoolExecutor(a.workers) as ex:
    results = list(ex.map(run, suites))
for _, _, line in results: print(line)
print(f"DONE {sum(ok for _, ok, _ in results)}/{len(results)}")
