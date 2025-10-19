import platform, subprocess, json, shutil, os
from datetime import datetime

def _ps(cmd):
    """Run a PowerShell command and return text (or empty string)."""
    try:
        out = subprocess.check_output(["powershell","-NoProfile","-Command", cmd], text=True)
        return out.strip()
    except Exception:
        return ""

def create_snapshot():
    # Basic system info
    sysinfo = {
        "hostname": platform.node(),
        "os": platform.platform(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }

    # BIOS / SMBIOS
    bios = {
        "bios_version": _ps("(Get-CimInstance -ClassName Win32_BIOS).SMBIOSBIOSVersion"),
        "bios_vendor": _ps("(Get-CimInstance -ClassName Win32_BIOS).Manufacturer"),
        "bios_date": _ps("(Get-CimInstance -ClassName Win32_BIOS).ReleaseDate"),
        "smbios_major": _ps("(Get-CimInstance -ClassName Win32_ComputerSystemProduct).Version"),
        "board_product": _ps("(Get-CimInstance -ClassName Win32_BaseBoard).Product"),
        "board_vendor": _ps("(Get-CimInstance -ClassName Win32_BaseBoard).Manufacturer"),
        "board_sn": _ps("(Get-CimInstance -ClassName Win32_BaseBoard).SerialNumber"),
    }

    # MEI device & version (if present)
    mei = {
        "device_present": bool(_ps("(Get-PnpDevice -Class System | Where-Object {$_.FriendlyName -like '*Management Engine*' -or $_.FriendlyName -like '*MEI*'}).FriendlyName")),
        "driver_version": _ps("(Get-PnpDevice -Class System | Where-Object {$_.FriendlyName -like '*Management Engine*' -or $_.FriendlyName -like '*MEI*'} | Get-PnpDeviceProperty DEVPKEY_Device_DriverVersion).Data"),
    }

    # CPU / Memory
    cpu = {
        "name": _ps("(Get-CimInstance Win32_Processor).Name"),
        "cores_logical": _ps("(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors"),
        "cores_physical": _ps("(Get-CimInstance Win32_Processor).NumberOfCores"),
    }
    mem = {
        "total_gb": _ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)"),
        "dimms": _ps("Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer,PartNumber,Speed,Capacity | ConvertTo-Json -Compress"),
    }

    # Storage (disks + boot)
    storage = {
        "boot_device": _ps("(Get-CimInstance Win32_OperatingSystem).SystemDrive"),
        "disks": _ps("Get-PhysicalDisk | Select-Object FriendlyName, MediaType, Size, SerialNumber | ConvertTo-Json -Compress"),
        "volumes": _ps("Get-Volume | Select-Object DriveLetter, FileSystemLabel, FileSystem, Size, SizeRemaining | ConvertTo-Json -Compress"),
    }

    # GPU
    gpu = {
        "adapters": _ps("Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate | ConvertTo-Json -Compress"),
    }

    # Network
    net = {
        "adapters": _ps("Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, MacAddress | ConvertTo-Json -Compress"),
    }

    snap = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": sysinfo,
        "bios": bios,
        "mei": mei,
        "cpu": cpu,
        "memory": mem,
        "storage": storage,
        "gpu": gpu,
        "network": net,
    }
    return snap
