package pk.edu.uos.bench.nativeandroid.export

import android.content.Context
import android.os.Build
import org.json.JSONObject
import pk.edu.uos.bench.nativeandroid.config.BenchmarkConfig
import pk.edu.uos.bench.nativeandroid.config.BenchmarkRegistry
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

data class BenchmarkRecord(
    val session: Int,
    val runId: String,
    val phase: String, // "warmup" | "measure" | "cold_start"
    val iteration: Int?,
    val inputIndex: Int?,
    val status: String = "ok",
    val errorMessage: String? = null,
    val preprocessMs: Double? = null,
    val inferenceMs: Double? = null,
    val inferenceNativeMs: Double? = null,
    val postprocessMs: Double? = null,
    val endToEndMs: Double? = null,
    val coldStartMs: Double? = null,
    val modelLoadMs: Double? = null,
    val pssMb: Double? = null,
    val cpuPct: Double? = null,
    val thermalStatus: String = "none",
    val outputDigest: String? = null
)

class JsonlExporter(
    private val context: Context,
    private val config: BenchmarkConfig
) {
    private val isoFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
        timeZone = TimeZone.getTimeZone("UTC")
    }
    private val fileDateFormat = SimpleDateFormat("yyyyMMdd", Locale.US)

    private val records = mutableListOf<BenchmarkRecord>()

    fun addRecord(record: BenchmarkRecord) {
        records.add(record)
    }

    fun flushToFile(): File {
        val today = fileDateFormat.format(Date())
        val deviceId = "dev-${Build.MANUFACTURER.lowercase().replace(" ", "-")}-${Build.MODEL.lowercase().replace(" ", "-")}"
        val fileName = "${today}_${config.platform}_${config.modelId}_${config.precision}_${config.delegate}_s%02d.jsonl".format(config.session)

        val outDir = File(context.getExternalFilesDir(null), "results")
        outDir.mkdirs()
        val outFile = File(outDir, fileName)

        FileWriter(outFile, true).use { writer ->
            for (r in records) {
                val json = JSONObject().apply {
                    put("schema_version", BenchmarkRegistry.SCHEMA_VERSION)
                    put("protocol_version", BenchmarkRegistry.PROTOCOL_VERSION)
                    put("synthetic", false)
                    put("timestamp_utc", isoFormat.format(Date()))
                    put("device_id", deviceId)
                    put("os", "android")
                    put("os_version", Build.VERSION.RELEASE)
                    put("api_level", Build.VERSION.SDK_INT)
                    put("app_version", "1.0.0")
                    put("build_mode", "release")
                    put("platform", config.platform)
                    put("runtime", "litert")
                    put("runtime_version", "2.16.1")
                    put("model_id", config.modelId)
                    put("precision", config.precision)
                    put("delegate", config.delegate)
                    put("cpu_threads", config.threads)
                    put("session", r.session)
                    put("run_id", r.runId)
                    put("phase", r.phase)

                    if (r.iteration != null) put("iteration", r.iteration)
                    if (r.inputIndex != null) put("input_index", r.inputIndex)
                    put("status", r.status)
                    if (r.errorMessage != null) put("error_message", r.errorMessage)

                    if (r.preprocessMs != null) put("preprocess_ms", roundMs(r.preprocessMs))
                    if (r.inferenceMs != null) put("inference_ms", roundMs(r.inferenceMs))
                    if (r.inferenceNativeMs != null) put("inference_native_ms", roundMs(r.inferenceNativeMs))
                    if (r.postprocessMs != null) put("postprocess_ms", roundMs(r.postprocessMs))
                    if (r.endToEndMs != null) put("end_to_end_ms", roundMs(r.endToEndMs))

                    if (r.coldStartMs != null) put("cold_start_ms", roundMs(r.coldStartMs))
                    if (r.modelLoadMs != null) put("model_load_ms", roundMs(r.modelLoadMs))
                    if (r.pssMb != null) put("pss_mb", roundMb(r.pssMb))
                    if (r.cpuPct != null) put("cpu_pct", roundMb(r.cpuPct))
                    put("thermal_status", r.thermalStatus)
                    if (r.outputDigest != null) put("output_digest", r.outputDigest)
                }
                writer.write(json.toString() + "\n")
            }
        }
        records.clear()
        return outFile
    }

    private fun roundMs(value: Double): Double = Math.round(value * 1000.0) / 1000.0
    private fun roundMb(value: Double): Double = Math.round(value * 100.0) / 100.0
}
