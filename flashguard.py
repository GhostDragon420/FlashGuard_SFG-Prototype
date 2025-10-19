#!/usr/bin/env python3
import argparse, json, time, os, sys
from pathlib import Path
from snapshot import create_snapshot
from validators import validate_payload
from plan import build_post_flash_plan

STATE_DIR = Path("state")
SNAP_DIR = STATE_DIR / "snapshots"
PLANS_DIR = STATE_DIR / "plans"
STATE_DIR.mkdir(exist_ok=True)
SNAP_DIR.mkdir(parents=True, exist_ok=True)
PLANS_DIR.mkdir(parents=True, exist_ok=True)

def cmd_snapshot(args):
    snap = create_snapshot()
    ts = time.strftime("%Y%m%d-%H%M%S")
    host = snap.get("system", {}).get("hostname", "host")
    out = SNAP_DIR / f"{host}-{ts}.json"
    out.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(f"[OK] Snapshot saved: {out}")

def cmd_validate(args):
    payload_path = Path(args.payload)
    ok, info = validate_payload(payload_path)
    print(json.dumps(info, indent=2))
    if not ok:
        sys.exit(2)

def cmd_plan(args):
    plan = build_post_flash_plan(
        desired_xmp=args.xmp,
        desired_boot=args.boot,
        rebar=args.rebar,
        secureboot=args.secureboot,
    )
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = PLANS_DIR / f"postflash-plan-{ts}.json"
    out.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"[OK] Plan saved: {out}")

def main():
    p = argparse.ArgumentParser(prog="flashguard", description="SFG-FlashGuard Prototype")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("snapshot", help="Collect a firmware/hardware snapshot")
    s1.set_defaults(func=cmd_snapshot)

    s2 = sub.add_parser("validate", help="Validate a (mock) firmware payload JSON")
    s2.add_argument("--payload", required=True, help="Path to firmware payload descriptor (JSON)")
    s2.set_defaults(func=cmd_validate)

    s3 = sub.add_parser("plan", help="Generate a post-flash restore plan (no writes)")
    s3.add_argument("--xmp", type=int, default=0, help="Target XMP MHz (e.g., 3200). 0=leave")
    s3.add_argument("--boot", type=str, default="", help="Primary boot device hint (e.g., nvme:CT1000P3PSSD8)")
    s3.add_argument("--rebar", choices=["on","off","leave"], default="leave", help="Resizable BAR setting")
    s3.add_argument("--secureboot", choices=["on","off","leave"], default="leave", help="Secure Boot setting")
    s3.set_defaults(func=cmd_plan)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
