package pk.edu.uos.bench.flutter_bench

import android.app.ActivityManager
import android.content.Context
import android.os.BatteryManager
import android.os.Build
import android.os.PowerManager
import android.os.Process
import android.os.SystemClock
import android.view.WindowManager
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private val CHANNEL = "pk.edu.uos.bench/metrics"
    private var lastProcessCpuTime: Long = 0
    private var lastCpuSampleTime: Long = 0

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "getPssMb" -> {
                    val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
                    val memInfo = am.getProcessMemoryInfo(intArrayOf(Process.myPid()))
                    val pss = if (memInfo.isNotEmpty()) memInfo[0].totalPss / 1024.0 else 0.0
                    result.success(pss)
                }
                "getCpuPct" -> {
                    val now = SystemClock.elapsedRealtime()
                    val cpuTime = readProcSelfStatCpuTime()
                    val deltaWall = now - lastCpuSampleTime
                    val deltaCpu = cpuTime - lastProcessCpuTime
                    lastProcessCpuTime = cpuTime
                    lastCpuSampleTime = now
                    val pct = if (deltaWall > 0 && deltaCpu >= 0) (deltaCpu.toDouble() / deltaWall.toDouble()) * 100.0 else 0.0
                    result.success(pct)
                }
                "getThermalStatus" -> {
                    val status = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
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
                    } else "none"
                    result.success(status)
                }
                "getBatteryChargeUah" -> {
                    val bm = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
                    val charge = bm.getLongProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER)
                    result.success(if (charge != Long.MIN_VALUE) charge else 0L)
                }
                "getDeviceId" -> {
                    val mfr = Build.MANUFACTURER.lowercase().replace("[^a-z0-9]+".toRegex(), "-").trim('-')
                    val rawModel = Build.MODEL.lowercase().replace("[^a-z0-9]+".toRegex(), "-").trim('-')
                    val cleanModel = if (rawModel.startsWith(mfr)) rawModel.removePrefix(mfr).trim('-') else rawModel
                    val deviceId = "dev-$mfr-$cleanModel"
                    result.success(deviceId)
                }
                "getOsVersion" -> {
                    result.success(Build.VERSION.RELEASE)
                }
                "getApiLevel" -> {
                    result.success(Build.VERSION.SDK_INT)
                }
                "getIntentExtras" -> {
                    val session = intent.getIntExtra("session", 1)
                    val autorun = intent.getBooleanExtra("autorun", false)
                    result.success(mapOf("session" to session, "autorun" to autorun))
                }
                "log" -> {
                    val msg = call.argument<String>("message") ?: ""
                    android.util.Log.i("BENCH", msg)
                    result.success(true)
                }
                "finish" -> {
                    finish()
                    result.success(true)
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun readProcSelfStatCpuTime(): Long {
        return try {
            val stat = File("/proc/self/stat").readText().trim().split("\\s+".toRegex())
            if (stat.size >= 15) {
                (stat[13].toLong() + stat[14].toLong()) * 10L
            } else 0L
        } catch (e: Exception) {
            0L
        }
    }
}

