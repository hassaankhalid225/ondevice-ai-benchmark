---
name: run-experiment
description: Plan, run and log a data-collection campaign on physical devices following the protocol. Use when collecting benchmark data, preparing a device, or pulling results into data/raw.
---

# Run an Experiment

## 1. Before
1. Check the device is registered in `docs/04-device-matrix.md` (else register it).
2. Copy `experiments/EXP-template.md` to `experiments/EXP-<next>.md`; fill header (builds,
   commits, toolchain, protocol version, seeds). Add a row in `experiments/README.md`.
3. Confirm the parity checklist has passed for these app builds (harness-contract §6).
4. Device prep (methodology §3):
   - reboot · battery 50–90 % · airplane mode · Wi-Fi/BT/location off · auto-sync off
   - brightness 50 %, auto-brightness off · close all apps · thermal status none/light
   - plugged for latency runs, **unplugged** for energy runs

## 2. Run
```bash
adb devices
adb shell dumpsys thermalservice | grep -i status       # wait for status 0/1
# per session k = 1..5, per app:
adb shell am force-stop <pkg>
adb shell am start -W -n <pkg>/.MainActivity --ei session <k> --ez autorun true
# wait for "DONE" in logcat:
adb logcat -s BENCH:I
adb pull /sdcard/Android/data/<pkg>/files/results/ data/raw/<device_id>/
```
- Alternate which platform goes first per session (randomised order is inside the app;
  app order across sessions: odd sessions Flutter first, even sessions native first).
- Note anything unusual in the EXP log with a timestamp.

## 3. After
1. `make validate`: fix nothing in raw files. If invalid, note it in the EXP log and fix the app.
2. Check thermal exclusions: sessions reaching `severe` → add to `data/exclusions.yaml`.
3. Complete the EXP log (output files, deviations, outcome).
4. Commit: `data(exp-NNN): <device> sessions 1-5`.
5. Update `docs/PROGRESS.md` → "Data collected".

## Never
- Never edit, rename, merge or delete files in `data/raw/`.
- Never collect with debug builds or with the phone charging during energy runs.
- Never mix protocol versions inside one EXP.
