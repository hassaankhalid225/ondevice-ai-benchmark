from unittest.mock import MagicMock, patch

from benchkit.runner import (
    find_adb,
    get_connected_devices,
    inspect_device,
    preflight_check,
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

