import json, hashlib
from pathlib import Path

def sha256sum(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_payload(payload_json_path: Path):
    """Validate a mock firmware payload descriptor.
    Expected schema:
    {
      "platform": {"board":"ROG STRIX Z490-H GAMING", "vendor":"ASUS", "min_bios":"2401"},
      "me": {"required": true, "min_version": "2316.5.0.0"},
      "file": {"path": "firmware/ROG-Z490H-3201.CAP", "sha256": "<hash>"}
    }
    """
    info = {"ok": False, "errors": [], "warnings": []}
    try:
        meta = json.loads(payload_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        info["errors"].append(f"Invalid JSON: {e}")
        return False, info

    file_path = Path(meta.get("file",{}).get("path",""))
    expected_hash = meta.get("file",{}).get("sha256","")
    if not file_path.exists():
        info["errors"].append(f"Payload file not found: {file_path}")
    else:
        actual = sha256sum(file_path)
        if expected_hash and expected_hash.lower() != actual.lower():
            info["errors"].append("SHA256 mismatch")
        info["file_hash"] = actual

    # Minimal semantic checks (real build would read live snapshot)
    platform = meta.get("platform",{})
    if platform.get("board","").strip() == "":
        info["warnings"].append("No board name in payload metadata.")
    if platform.get("vendor","").upper() not in ("ASUS","MSI","GIGABYTE","ASROCK","LENOVO","DELL","HP",""):
        info["warnings"].append("Unknown vendor in payload metadata.")

    info["ok"] = len(info["errors"]) == 0
    return info["ok"], info
