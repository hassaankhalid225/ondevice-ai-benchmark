package pk.edu.uos.bench.nativeandroid.metrics

import android.app.ActivityManager
import android.content.Context
import android.os.BatteryManager
import android.os.Build
import android.os.Debug
import android.os.PowerManager
import android.os.Process
import android.os.SystemClock
import java.io.File

object SystemMetrics {

    private var lastProcessCpuTime: Long = 0
    private var lastCpuSampleTime: Long = 0

    init {
        sampleCpuDelta()
    }

    fun getPssMb(context: Context): Double {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memInfo = am.getProcessMemoryInfo(intArrayOf(Process.myPid()))
        return if (memInfo.isNotEmpty()) {
            memInfo[0].totalPss / 1024.0 // KB -> MB
        } else {
            0.0
        }
    }

    /**
     * Reads process user and system time from /proc/self/stat and computes CPU %.
     */
    fun sampleCpuDelta(): Double {
        val now = SystemClock.elapsedRealtime()
        val cpuTime = readProcSelfStatCpuTime()
        val deltaWallMs = now - lastCpuSampleTime
        val deltaCpuMs = cpuTime - lastProcessCpuTime

        lastProcessCpuTime = cpuTime
        lastCpuSampleTime = now

        return if (deltaWallMs > 0 && deltaCpuMs >= 0) {
            (deltaCpuMs.toDouble() / deltaWallMs.toDouble()) * 100.0
        } else {
            0.0
        }
    }

    private fun readProcSelfStatCpuTime(): Long {
        return try {
            val stat = File("/proc/self/stat").readText().trim().split("\\s+".toRegex())
            if (stat.size >= 15) {
                // utime is field 14 (index 13), stime is field 15 (index 14) in clock ticks
                val utimeTicks = stat[13].toLong()
                val stimeTicks = stat[14].toLong()
                // Standard Linux clock tick is 100 Hz (10 ms per tick)
                (utimeTicks + stimeTicks) * 10L
            } else {
                0L
            }
        } catch (e: Exception) {
            0L
        }
    }

    fun getThermalStatus(context: Context): String {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val pm = context.getSystemService(Context.POWER_SERVICE) as PowerManager
            when (pm.currentThermalStatus) {
                PowerManager.THERMAL_STATUS_NONE -> "none"
                PowerManager.THERMAL_STATUS_LIGHT -> "light"
                PowerManager.THERMAL_STATUS_MODERATE -> "moderate"
                PowerManager.THERMAL_STATUS_SEVERE -> "severe"
                PowerManager.THERMAL_STATUS_CRITICAL -> "critical"
                PowerManager.THERMAL_STATUS_EMERGENCY -> "emergency"
                PowerManager.THERMAL_STATUS_SHUTDOWN -> "shutdown"
                else -> "unknown"
            }
        } else {
            "none"
        }
    }

    fun getBatteryChargeUah(context: Context): Long {
        val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        val chargeUah = bm.getLongProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER)
        return if (chargeUah != Long.MIN_VALUE) chargeUah else 0L
    }
}
