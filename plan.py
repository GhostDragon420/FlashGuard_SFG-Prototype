from datetime import datetime

def build_post_flash_plan(desired_xmp: int = 0, desired_boot: str = "", rebar: str = "leave", secureboot: str = "leave"):
    """Return a dict representing a post-flash restore plan.
    NOTE: This does not write anything; it's a declarative plan.
    """
    steps = []
    if desired_boot:
        steps.append({"action":"set_boot_order", "primary": desired_boot})
    if desired_xmp:
        steps.append({"action":"set_memory_xmp", "profile_mhz": desired_xmp})
    if rebar in ("on","off"):
        steps.append({"action":"set_rebar", "value": rebar})
    if secureboot in ("on","off"):
        steps.append({"action":"set_secure_boot", "value": secureboot})

    # Always include sanity checks
    steps.extend([
        {"action":"verify_mei_driver", "min_version":"2316.5.0.0"},
        {"action":"verify_gpu_link", "expected":"PCIe Gen3/4 x16"},
        {"action":"verify_nvme_boot", "device_hint": desired_boot or "nvme"},
    ])

    return {
        "generated": datetime.utcnow().isoformat() + "Z",
        "policy_version": "0.1",
        "steps": steps,
        "notes": [
            "This is a dry-run declarative plan. Another module would translate to vendor-specific calls.",
            "On ASUS, boot order + XMP + ReBAR typically require AMI/ASUS tools or direct EFI var writes.",
        ]
    }
