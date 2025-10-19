# SFG-FlashGuard (Prototype v0.1)

**Goal:** Make BIOS/ME flashes fast, predictable, and (eventually) one‑click by
snapshooting your current firmware/hardware state, validating payloads, and restoring
safe settings after a reboot.

> This is a **prototype skeleton**. It doesn’t flash anything yet. It creates a “snapshot”
> JSON, validates a pretend payload, and outlines where ME/EFI hooks would go.

## What it does today
- Collects a *hardware/firmware* snapshot using Windows-safe commands (WMI/PowerShell).
- Saves results in `./state/snapshots/<hostname>-<timestamp>.json`.
- Validates a mock firmware payload file (hash + compatibility fields).
- Prepares a “post-flash plan” with boot order, memory profile, and fan curve hints.

## Roadmap (high level)
1. **MEI / FW Tooling**
   - Detect Intel MEI driver + version (WMI device query).
   - Add wrappers for `FWUpdLcl64.exe` (Intel ME firmware) and OEM BIOS CLI tools.
2. **EFI variable I/O**
   - Read/write NVRAM: boot order, SecureBoot mode, Re‑BAR, XMP status (vendor-specific).
3. **Policy Engine**
   - Compare pre‑flash snapshot with post‑flash platform map to reapply only safe params.
4. **Rollback**
   - Keep last known-good BIOS config + ME region checksum; auto-rollback on failure.

## Usage
```bash
# 1) Create a snapshot
python flashguard.py snapshot

# 2) Validate a (mock) payload
python flashguard.py validate --payload samples/mock_firmware_payload.json

# 3) Plan a post-flash restore
python flashguard.py plan --xmp 3200 --boot nvme:CT1000P3PSSD8 --rebar on
```

## Notes
- Windows-only for now (PowerShell calls). Linux/Mac support planned.
- This is *read-only* and safe. No firmware writes.
- All results go to `./state/`.

