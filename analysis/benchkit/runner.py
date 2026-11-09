"""ADB-based experiment automation and device orchestration.

Provides automated pre-flight checks, APK deployment, session execution,
result extraction, and validation conforming to protocol v0.3.0.
"""

from __future__ import annotations

import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from . import RAW_DIR
from .validate import load_validator, validate_file

NATIVE_PKG = "pk.edu.uos.bench.nativeandroid"
NATIVE_ACT = "pk.edu.uos.bench.nativeandroid/.ui.MainActivity"
NATIVE_APK = Path("apps/android_native_bench/app/build/outputs/apk/release/app-release.apk")

FLUTTER_PKG = "pk.edu.uos.bench.flutter_bench"
FLUTTER_ACT = "pk.edu.uos.bench.flutter_bench/.MainActivity"
FLUTTER_APK = Path("apps/flutter_bench/build/app/outputs/flutter-apk/app-release.apk")


def find_adb() -> str:
    """Locate adb binary across PATH and standard Android SDK locations."""
    which_adb = shutil.which("adb")
    if which_adb:
        return which_adb

    candidates = [
        Path(os.environ.get("ANDROID_HOME", "")) / "platform-tools" / "adb.exe",
        Path(os.environ.get("ANDROID_SDK_ROOT", "")) / "platform-tools" / "adb.exe",
        Path.home() / "AppData" / "Local" / "Android" / "Sdk" / "platform-tools" / "adb.exe",
        Path("C:/Users/FINELA~1/AppData/Local/Android/Sdk/platform-tools/adb.exe"),
        Path("C:/Users/FINE LAPTOP/AppData/Local/Android/Sdk/platform-tools/adb.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c.resolve())

    raise FileNotFoundError("adb executable not found. Ensure Android SDK platform-tools are in PATH.")


def run_adb(args: list[str], device_serial: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Execute an ADB command."""
    adb = find_adb()
    cmd = [adb]
    if device_serial:
        cmd.extend(["-s", device_serial])
    cmd.extend(args)
    return subprocess.run(cmd, capture_output=True, text=True, check=check, encoding="utf-8", errors="replace")


def get_connected_devices() -> list[dict[str, str]]:
    """List all connected ADB devices and their state."""
    res = run_adb(["devices", "-l"])
    devices = []
    for line in res.stdout.strip().splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        serial = parts[0]
        state = parts[1]
        extra = " ".join(parts[2:])
        devices.append({"serial": serial, "state": state, "info": extra})
    return devices


def inspect_device(serial: str | None = None) -> dict[str, Any]:
    """Extract hardware and OS properties to register device in docs/04-device-matrix.md."""
    import re

    def prop(name: str) -> str:
        r = run_adb(["shell", "getprop", name], device_serial=serial, check=False)
        return r.stdout.strip()

    brand = re.sub(r"[^a-z0-9]+", "-", prop("ro.product.brand").lower()).strip("-")
    raw_model = re.sub(r"[^a-z0-9]+", "-", prop("ro.product.model").lower()).strip("-")
    clean_model = raw_model[len(brand):].strip("-") if raw_model.startswith(brand) else raw_model
    dev_id = f"dev-{brand}-{clean_model}"
    soc = prop("ro.soc.model") or prop("ro.board.platform")
    release = prop("ro.build.version.release")
    sdk = prop("ro.build.version.sdk")

    # RAM from /proc/meminfo
    mem_res = run_adb(["shell", "cat", "/proc/meminfo"], device_serial=serial, check=False)
    total_ram_gb = "unknown"
    for mline in mem_res.stdout.splitlines():
        if mline.startswith("MemTotal:"):
            kb = int(mline.split()[1])
            total_ram_gb = f"{round(kb / (1024 * 1024), 1)} GB"
            break

    return {
        "device_id": dev_id,
        "brand": brand,
        "model": clean_model,
        "soc": soc,
        "ram": total_ram_gb,
        "os": f"Android {release} (API {sdk})",
        "serial": serial,
    }


def preflight_check(serial: str | None = None) -> bool:
    """Run environmental checks per methodology §3."""
    print("--- Running Pre-Flight Environmental Checks ---")
    ok = True

    # Battery
    bat = run_adb(["shell", "dumpsys", "battery"], device_serial=serial, check=False).stdout
    level = None
    plugged = False
    for line in bat.splitlines():
        if "level:" in line:
            level = int(line.split(":")[1].strip())
        if "AC powered: true" in line or "USB powered: true" in line or "Wireless powered: true" in line:
            plugged = True

    print(f"  Battery Level: {level}% (plugged: {plugged})")
    if level is not None and level < 50:
        print("  [WARN] Battery level < 50%. Charge device before full session runs.")
        ok = False

    # Thermal
    thermal = run_adb(["shell", "dumpsys", "thermalservice"], device_serial=serial, check=False).stdout
    thermal_status = "unknown"
    for line in thermal.splitlines():
        if "status:" in line.lower() or "thermalstatus" in line.lower():
            thermal_status = line.strip()
            break
    print(f"  Thermal State: {thermal_status}")

    # Airplane mode
    airplane = run_adb(["shell", "settings", "get", "global", "airplane_mode_on"], device_serial=serial, check=False).stdout.strip()
    is_airplane = airplane == "1"
    print(f"  Airplane Mode: {'ON' if is_airplane else 'OFF (recommended ON)'}")

    return ok


def install_apks(serial: str | None = None) -> None:
    """Install release APKs on connected device."""
    if not NATIVE_APK.is_file():
        raise FileNotFoundError(f"Native APK not found at {NATIVE_APK}. Run gradlew assembleRelease first.")
    if not FLUTTER_APK.is_file():
        raise FileNotFoundError(f"Flutter APK not found at {FLUTTER_APK}. Run flutter build apk --release first.")

    print(f"Installing Android Native APK ({NATIVE_APK.name})...")
    run_adb(["install", "-r", "-g", str(NATIVE_APK.resolve())], device_serial=serial)
    print("Android Native APK installed successfully.")

    print(f"Installing Flutter APK ({FLUTTER_APK.name})...")
    run_adb(["install", "-r", "-g", str(FLUTTER_APK.resolve())], device_serial=serial)
    print("Flutter APK installed successfully.")


def run_single_app(pkg: str, act: str, session: int, serial: str | None = None) -> None:
    """Execute one benchmark app headless session and wait for completion."""
    print(f"\n[RUN] Stopping {pkg}...")
    run_adb(["shell", "am", "force-stop", pkg], device_serial=serial, check=False)
    time.sleep(2)

    # Clear logcat
    run_adb(["logcat", "-c"], device_serial=serial, check=False)

    print(f"[RUN] Starting {pkg} Session {session} in autorun mode...")
    start_cmd = [
        "shell", "am", "start", "-W",
        "-n", act,
        "--ei", "session", str(session),
        "--ez", "autorun", "true",
    ]
    run_adb(start_cmd, device_serial=serial)

    print("[RUN] App started. Streaming logs until completion...")
    adb_bin = find_adb()
    cmd = [adb_bin]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["logcat", "-s", "BENCH:I"])

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")

    def _stream(p: subprocess.Popen[str], q: queue.Queue[str]) -> None:
        try:
            assert p.stdout is not None
            for line in p.stdout:
                q.put(line)
        except Exception:
            pass

    log_q: queue.Queue[str] = queue.Queue()
    t = threading.Thread(target=_stream, args=(proc, log_q), daemon=True)
    t.start()

    last_log_time = time.time()
    try:
        while True:
            try:
                line = log_q.get(timeout=2.0)
                sys.stdout.write(line)
                sys.stdout.flush()
                last_log_time = time.time()
                if "Session" in line and ("Completed" in line or "Finished" in line):
                    print(f"[DONE] Completion signal observed for {pkg}.")
                    break
            except queue.Empty:
                # Check if process is still alive on device
                res = run_adb(["shell", "pidof", pkg], device_serial=serial, check=False)
                if not res.stdout.strip():
                    print(f"\n[INFO] Process {pkg} exited on device.")
                    break
                if time.time() - last_log_time > 300:
                    print(f"\n[WARN] Watchdog timeout: 5 minutes idle for {pkg}.")
                    break
    finally:
        proc.kill()


def pull_results(pkg: str, device_id: str, serial: str | None = None) -> list[Path]:
    """Pull generated JSONL results from device to data/raw/<device_id>/."""
    dest_dir = RAW_DIR / device_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    dev_results_dir = f"/sdcard/Android/data/{pkg}/files/results"
    print(f"\n[PULL] Pulling results from {dev_results_dir}/. -> {dest_dir}...")
    run_adb(["pull", f"{dev_results_dir}/.", str(dest_dir.resolve())], device_serial=serial, check=False)

    # Flatten if ADB created a nested results folder
    nested = dest_dir / "results"
    if nested.is_dir():
        for f in nested.glob("*.jsonl"):
            target = dest_dir / f.name
            if target.exists():
                target.unlink()
            f.rename(target)
        shutil.rmtree(nested, ignore_errors=True)

    pulled = list(dest_dir.glob("*.jsonl"))
    print(f"[PULL] {len(pulled)} JSONL result files present in {dest_dir}.")
    return pulled


def run_session(session: int, device_id: str, serial: str | None = None) -> None:
    """Execute a complete session alternating platform order per protocol §4."""
    preflight_check(serial)

    # Alternate platform order across sessions
    # Odd sessions: Flutter first; Even sessions: Native first
    if session % 2 == 1:
        order = [("flutter", FLUTTER_PKG, FLUTTER_ACT), ("native", NATIVE_PKG, NATIVE_ACT)]
    else:
        order = [("native", NATIVE_PKG, NATIVE_ACT), ("flutter", FLUTTER_PKG, FLUTTER_ACT)]

    print("\n=======================================================")
    print(f"  Starting Experiment Session {session} on {device_id}")
    print(f"  Execution Order: {[p[0] for p in order]}")
    print("=======================================================")

    for name, pkg, act in order:
        print(f"\n>>> Executing {name.upper()} suite ({pkg}) <<<")
        run_single_app(pkg, act, session, serial)
        pull_results(pkg, device_id, serial)

    print("\n--- Validating Pulled Results ---")
    valid_count = 0
    all_files = list((RAW_DIR / device_id).glob(f"*_s{session:02d}.jsonl"))
    if not all_files:
        all_files = list((RAW_DIR / device_id).glob("*.jsonl"))

    validator = load_validator()
    for f in all_files:
        report = validate_file(f, validator)
        status = "OK" if report.ok else "FAIL"
        print(f"[{status}] {f.name} ({report.n_records} records)")
        if report.ok:
            valid_count += 1
        else:
            for err in report.errors:
                print(f"       ERROR: {err}")

    print(f"\nSession {session} complete: {valid_count}/{len(all_files)} files valid.")
