"""
Autonomous multi-session runner for Infinix Smart 7 (dev-infinix-x6515)
Branch: exp-002, Arm: smart7_full
Executes remaining Sessions 7 & 8 with battery protection and Smart 7 serial targeting.
"""
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = ANALYSIS_DIR.parent
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from benchkit.runner import run_session, run_adb, find_adb
from benchkit.validate import validate_tree

DEVICE_ID = "dev-infinix-x6515"
PHONE_IP = "192.168.43.185"
ARM = "smart7_full"
THREADS = 4
BATTERY_MIN_THRESHOLD = 3  # Safety cutoff at 3%

HOT8_SERIAL = "047252506A023336"  # USB Hot 8 to exclude

def get_active_serial() -> str:
    """Find current working serial for Smart 7 (excluding Hot 8)."""
    try:
        adb = find_adb()
        import subprocess
        res = subprocess.run([adb, "devices"], capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "device":
                serial = parts[0]
                if serial == HOT8_SERIAL:
                    continue
                return serial
    except Exception:
        pass
    return ""

def reconnect_if_needed() -> str:
    """Ensure Smart 7 is connected; scan wireless port and reconnect if dropped."""
    serial = get_active_serial()
    if serial:
        return serial

    print(f"[RECONNECT] Smart 7 offline. Scanning ports on {PHONE_IP}...", flush=True)
    open_ports = []
    def check_port(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        if s.connect_ex((PHONE_IP, p)) == 0:
            open_ports.append(p)
        s.close()

    with ThreadPoolExecutor(max_workers=100) as ex:
        ex.map(check_port, range(30000, 50000))

    if open_ports:
        port = open_ports[0]
        print(f"[RECONNECT] Discovered open wireless debugging port {port}. Connecting...", flush=True)
        run_adb(["connect", f"{PHONE_IP}:{port}"], check=False)
        time.sleep(3)

    return get_active_serial()

def get_battery_level(serial: str) -> int | None:
    try:
        res = run_adb(["shell", "dumpsys", "battery"], device_serial=serial, check=False)
        for line in res.stdout.splitlines():
            if "level:" in line:
                return int(line.split(":")[1].strip())
    except Exception as e:
        print(f"[BATTERY ERROR] {e}", flush=True)
    return None

def wake_screen(serial: str):
    try:
        run_adb(["shell", "input", "keyevent", "KEYCODE_WAKEUP"], device_serial=serial, check=False)
        run_adb(["shell", "wm", "dismiss-keyguard"], device_serial=serial, check=False)
        run_adb(["shell", "settings", "put", "system", "screen_off_timeout", "2147483647"], device_serial=serial, check=False)
        run_adb(["shell", "svc", "power", "stayon", "true"], device_serial=serial, check=False)
    except Exception:
        pass

def main():
    log_file = ANALYSIS_DIR / "auto_run_smart7.log"
    def log(msg: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line, flush=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    log("\n=======================================================")
    log("=== Starting Final Campaign Sessions (S7 & S8) for Smart 7 ===")
    log("=======================================================")

    serial = reconnect_if_needed()
    if not serial:
        log("[FATAL] Could not connect to Infinix Smart 7. Aborting.")
        return

    wake_screen(serial)
    bat = get_battery_level(serial)
    log(f"Active Serial: {serial} | Battery Level: {bat}%")

    if bat is None or bat <= BATTERY_MIN_THRESHOLD:
        log(f"Battery too low ({bat}% <= {BATTERY_MIN_THRESHOLD}%). Exiting.")
        return

    # Plan: Sessions 7 and 8
    plan = [
        (7, "both"),
        (8, "both"),
    ]

    for session_idx, platform_filter in plan:
        serial = reconnect_if_needed()
        if not serial:
            log("[WARN] Connection lost. Retrying in 15 seconds...")
            time.sleep(15)
            serial = reconnect_if_needed()
            if not serial:
                log("[FATAL] Unable to re-establish ADB connection. Halting.")
                break

        wake_screen(serial)
        bat = get_battery_level(serial)
        log(f"\n-----------------------------------------------------------")
        log(f"Preparing Session {session_idx} [Platform: {platform_filter}]")
        log(f"Current Battery: {bat}% (Cutoff threshold: >{BATTERY_MIN_THRESHOLD}%)")
        if bat is not None and bat <= BATTERY_MIN_THRESHOLD:
            log(f"[STOP] Battery reached threshold ({bat}%). Stopping safely.")
            break

        log(f">>> LAUNCHING Session {session_idx} [Platform: {platform_filter}, Threads: {THREADS}, Arm: {ARM}] <<<")
        start_t = time.time()
        try:
            run_session(
                session=session_idx,
                device_id=DEVICE_ID,
                serial=serial,
                threads=THREADS,
                cpu_only=False,
                loader="asset",
                arm=ARM,
                platform_filter=platform_filter,
            )
            elapsed = time.time() - start_t
            log(f">>> Session {session_idx} ({platform_filter}) FINISHED in {elapsed/60:.1f} minutes <<<")
        except Exception as e:
            log(f"[SESSION ERROR] Session {session_idx} ({platform_filter}) failed: {e}")
            time.sleep(10)

        # Post-session battery & validation
        serial = reconnect_if_needed()
        bat_after = get_battery_level(serial) if serial else None
        consumed = (bat - bat_after) if (bat is not None and bat_after is not None) else "N/A"
        log(f"Post-Session Battery: {bat_after}% (Consumed: {consumed}%)")

        raw_dest = REPO_ROOT / "data" / "raw" / "exp002" / ARM / DEVICE_ID
        try:
            reports = validate_tree(raw_dest)
            valid_n = sum(1 for r in reports if r.ok)
            log(f"Validation update for {raw_dest.name}: {valid_n}/{len(reports)} files valid.")
        except Exception as ve:
            log(f"Validation error: {ve}")

    log("\n=== All Target Benchmark Sessions (1 through 8) Complete! ===")
    try:
        if serial:
            run_adb(["shell", "svc", "power", "stayon", "false"], device_serial=serial, check=False)
    except Exception:
        pass

if __name__ == "__main__":
    main()
