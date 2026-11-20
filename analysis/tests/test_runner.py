from pathlib import Path
from unittest.mock import MagicMock, patch

from benchkit import RAW_DIR
from benchkit.runner import (
    _resolve_dest_dir,
    find_adb,
    get_connected_devices,
    inspect_device,
    preflight_check,
    pull_results,
    run_single_app,
)


def test_find_adb():
    adb_path = find_adb()
    assert "adb" in adb_path.lower()


def test_get_connected_devices_empty():
    with patch("benchkit.runner.run_adb") as mock_run:
        mock_run.return_value = MagicMock(stdout="List of devices attached\n\n")
        devices = get_connected_devices()
        assert devices == []


def test_get_connected_devices_parsed():
    with patch("benchkit.runner.run_adb") as mock_run:
        mock_run.return_value = MagicMock(stdout="List of devices attached\nemulator-5554 device product:sdk_gphone64_arm64 model:sdk_gphone64_arm64\n")
        devices = get_connected_devices()
        assert len(devices) == 1
        assert devices[0]["serial"] == "emulator-5554"
        assert devices[0]["state"] == "device"


def test_inspect_device():
    def mock_run_adb(args, device_serial=None, check=True):
        if "ro.product.brand" in args:
            return MagicMock(stdout="Samsung\n")
        if "ro.product.model" in args:
            return MagicMock(stdout="Galaxy A14\n")
        if "ro.soc.model" in args:
            return MagicMock(stdout="Exynos 850\n")
        if "ro.build.version.release" in args:
            return MagicMock(stdout="13\n")
        if "ro.build.version.sdk" in args:
            return MagicMock(stdout="33\n")
        if "/proc/meminfo" in args:
            return MagicMock(stdout="MemTotal:        3982464 kB\nMemFree:          124500 kB\n")
        return MagicMock(stdout="")

    with patch("benchkit.runner.run_adb", side_effect=mock_run_adb):
        info = inspect_device("test-serial")
        assert info["device_id"] == "dev-samsung-galaxy-a14"
        assert info["soc"] == "Exynos 850"
        assert "3.8 GB" in info["ram"]
        assert "Android 13 (API 33)" in info["os"]


def test_preflight_check():
    def mock_run_adb(args, device_serial=None, check=True):
        if "battery" in args:
            return MagicMock(stdout="level: 85\nAC powered: false\nUSB powered: false\n")
        if "thermalservice" in args:
            return MagicMock(stdout="Status: 0\n")
        if "airplane_mode_on" in args:
            return MagicMock(stdout="1\n")
        return MagicMock(stdout="")

    with patch("benchkit.runner.run_adb", side_effect=mock_run_adb):
        ok = preflight_check("test-serial")
        assert ok is True


def test_session_platform_order():
    from benchkit.runner import FLUTTER_PKG, NATIVE_PKG
    # Session 1: odd -> flutter first
    order_1 = [("flutter", FLUTTER_PKG), ("native", NATIVE_PKG)] if 1 % 2 == 1 else [("native", NATIVE_PKG), ("flutter", FLUTTER_PKG)]
    assert order_1[0][0] == "flutter"
    assert order_1[1][0] == "native"

    # Session 2: even -> native first
    order_2 = [("flutter", FLUTTER_PKG), ("native", NATIVE_PKG)] if 2 % 2 == 1 else [("native", NATIVE_PKG), ("flutter", FLUTTER_PKG)]
    assert order_2[0][0] == "native"
    assert order_2[1][0] == "flutter"


def test_resolve_dest_dir_isolation():
    assert _resolve_dest_dir("dev-infinix-x650c") == RAW_DIR / "dev-infinix-x650c"
    assert _resolve_dest_dir("dev-infinix-x650c", arm="matched_1t") == RAW_DIR / "exp002" / "matched_1t" / "dev-infinix-x650c"


def test_run_single_app_intent_extras():
    called_cmds = []

    def mock_run_adb(args, device_serial=None, check=True):
        called_cmds.append(args)
        if args == ["shell", "pidof", "pk.edu.uos.bench.flutter_bench"]:
            return MagicMock(stdout="")
        return MagicMock(stdout="")

    mock_proc = MagicMock()
    mock_proc.stdout = ["01-01 00:00:00.000 I/BENCH: Status: Session 3 Completed!\n"]
    with (
        patch("benchkit.runner.run_adb", side_effect=mock_run_adb),
        patch("benchkit.runner.time.sleep"),
        patch("benchkit.runner.find_adb", return_value="adb"),
        patch("benchkit.runner.subprocess.Popen", return_value=mock_proc),
    ):
        run_single_app(
            "pk.edu.uos.bench.flutter_bench",
            "pk.edu.uos.bench.flutter_bench/.MainActivity",
            3,
            threads=1,
            cpu_only=True,
            loader="file",
        )

    am_start = next(c for c in called_cmds if len(c) > 2 and c[:3] == ["shell", "am", "start"])
    assert "--ei" in am_start and "threads" in am_start and "1" in am_start
    assert "--ez" in am_start and "cpuOnly" in am_start and "true" in am_start
    assert "--es" in am_start and "loader" in am_start and "file" in am_start


def test_pull_results_filters_session_and_isolates_arm(tmp_path):
    def mock_run_adb(args, device_serial=None, check=True):
        if args[0] == "pull":
            staging = Path(args[2])
            (staging / "20261112_flutter_mobilenetv3_large_fp32_cpu_s01.jsonl").write_text("{}\n", encoding="utf-8")
            (staging / "20261112_flutter_mobilenetv3_large_fp32_cpu_s02.jsonl").write_text("{}\n", encoding="utf-8")
        return MagicMock(stdout="")

    with (
        patch("benchkit.runner.RAW_DIR", tmp_path),
        patch("benchkit.runner.run_adb", side_effect=mock_run_adb),
    ):
        pulled = pull_results("pk.edu.uos.bench.flutter_bench", "dev-infinix-x650c", arm="matched_1t", session=1)

    assert len(pulled) == 1
    assert pulled[0].name.endswith("_s01.jsonl")
    assert pulled[0].parent == tmp_path / "exp002" / "matched_1t" / "dev-infinix-x650c"

