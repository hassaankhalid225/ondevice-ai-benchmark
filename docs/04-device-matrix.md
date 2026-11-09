# 04 · Device Matrix

Register every device here **before** collecting data on it. `device_id` is used in file
paths and in every record.

| device_id | Tier | Model | SoC | RAM | OS / API | Owner / source | Status |
|---|---|---|---|---|---|---|---|
| _dev-xxx-yyy_ | low | | | | | | planned |
| _dev-xxx-yyy_ | mid | | | | | | planned |
| _dev-xxx-yyy_ | high | | | | | | planned |
| _dev-apple-iphoneXX_ | iOS (optional) | | | | | | planned |

## Tier guidance
- **Low:** ≤ 4 GB RAM, entry SoC (e.g. Helio G/Unisoc/Snapdragon 4-series), the common
  phone in Pakistan, so it's highly relevant for the paper's practical message.
- **Mid:** 6–8 GB RAM, Snapdragon 6/7-series, Dimensity 7000-series.
- **High:** flagship SoC (Snapdragon 8-series, Dimensity 9000-series, Tensor).

## How to register a device
1. Pick `device_id` = `dev-<brand>-<model>` (lowercase, hyphens).
2. Collect: `adb shell getprop ro.product.model`, `ro.soc.model`, `ro.build.version.release`,
   `ro.build.version.sdk`, total RAM (`adb shell cat /proc/meminfo | head -1`).
3. Add a row above and set status `ready`.
4. Borrowed devices: note the owner and dates available. Factory-reset is not required, but
   uninstall heavy background apps or note them.
