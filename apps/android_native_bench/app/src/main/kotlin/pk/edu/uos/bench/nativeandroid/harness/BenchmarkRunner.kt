package pk.edu.uos.bench.nativeandroid.harness

import android.content.Context
import android.os.SystemClock
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.nnapi.NnApiDelegate
import pk.edu.uos.bench.nativeandroid.config.BenchmarkConfig
import pk.edu.uos.bench.nativeandroid.config.BenchmarkRegistry
import pk.edu.uos.bench.nativeandroid.export.BenchmarkRecord
import pk.edu.uos.bench.nativeandroid.export.JsonlExporter
import pk.edu.uos.bench.nativeandroid.metrics.SystemMetrics
import pk.edu.uos.bench.nativeandroid.tasks.BenchmarkTask
import pk.edu.uos.bench.nativeandroid.tasks.ClassificationTask
import pk.edu.uos.bench.nativeandroid.tasks.DetectionTask
import pk.edu.uos.bench.nativeandroid.tasks.QATask
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel
import java.util.UUID

class BenchmarkRunner(
    private val context: Context,
    private val onLog: (String) -> Unit = {}
) {

    fun runConfiguration(config: BenchmarkConfig): File {
        val runId = UUID.randomUUID().toString()
        val exporter = JsonlExporter(context, config)
        val spec = BenchmarkRegistry.getModelSpec(config.modelId)
        val isInt8 = config.precision == "int8"
        val modelAssetPath = if (isInt8) spec.int8File else spec.fp32File
        val expectedSha256 = if (isInt8) spec.int8Sha256 else spec.fp32Sha256

        onLog("[RUN] Starting ${config.modelId} (${config.precision}, ${config.delegate}) session ${config.session}")

        // 1. Verify model hash parity (contract §1)
        val verified = BenchmarkRegistry.verifyAssetSha256(context, modelAssetPath, expectedSha256)
        if (!verified) {
            val err = "Model SHA-256 verification failed for $modelAssetPath"
            onLog("[ERROR] $err")
            exporter.addRecord(
                BenchmarkRecord(
                    session = config.session,
                    runId = runId,
                    phase = "measure",
                    iteration = null,
                    inputIndex = null,
                    status = "error",
                    errorMessage = err
                )
            )
            return exporter.flushToFile()
        }

        // 2. Wait for thermal cooldown if needed (contract §2)
        var thermal = SystemMetrics.getThermalStatus(context)
        if (thermal == "moderate" || thermal == "severe" || thermal == "critical") {
            onLog("[THERMAL] Waiting for device cooldown (current: $thermal)...")
            var waitCount = 0
            while ((thermal == "moderate" || thermal == "severe" || thermal == "critical") && waitCount < 12) {
                Thread.sleep(5000)
                thermal = SystemMetrics.getThermalStatus(context)
                waitCount++
            }
        }

        // 3. Delegate & Interpreter creation
        var gpuDelegate: GpuDelegate? = null
        var nnapiDelegate: NnApiDelegate? = null
        val options = Interpreter.Options().apply {
            setNumThreads(config.threads)
            setUseXNNPACK(true)
        }

        try {
            when (config.delegate) {
                "gpu" -> {
                    val gpuOpts = GpuDelegate.Options().apply {
                        setPrecisionLossAllowed(config.precision == "fp16" || config.precision == "int8")
                    }
                    gpuDelegate = GpuDelegate(gpuOpts)
                    options.addDelegate(gpuDelegate)
                }
                "nnapi" -> {
                    val nnapiOpts = NnApiDelegate.Options().apply {
                        setAllowFp16(true)
                    }
                    nnapiDelegate = NnApiDelegate(nnapiOpts)
                    options.addDelegate(nnapiDelegate)
                }
            }
        } catch (e: Throwable) {
            val msg = "Delegate initialization unsupported: ${e.message}"
            onLog("[WARN] $msg")
            exporter.addRecord(
                BenchmarkRecord(
                    session = config.session,
                    runId = runId,
                    phase = "measure",
                    iteration = null,
                    inputIndex = null,
                    status = "unsupported",
                    errorMessage = msg
                )
            )
            return exporter.flushToFile()
        }

        // Load model buffer & measure model_load_ms
        val loadStartNanos = SystemClock.elapsedRealtimeNanos()
        val modelBuffer = loadModelFile(context, modelAssetPath)
        val interpreter = try {
            Interpreter(modelBuffer, options)
        } catch (e: Throwable) {
            val msg = "Interpreter creation unsupported for delegate ${config.delegate}: ${e.message}"
            onLog("[WARN] $msg")
            gpuDelegate?.close()
            nnapiDelegate?.close()
            exporter.addRecord(
                BenchmarkRecord(
                    session = config.session,
                    runId = runId,
                    phase = "measure",
                    iteration = null,
                    inputIndex = null,
                    status = "unsupported",
                    errorMessage = msg
                )
            )
            return exporter.flushToFile()
        }
        val loadEndNanos = SystemClock.elapsedRealtimeNanos()
        val modelLoadMs = (loadEndNanos - loadStartNanos) / 1e6

        // 4. Initialize task
        val task: BenchmarkTask = when (spec.task) {
            "classification" -> ClassificationTask(isInt8)
            "detection" -> DetectionTask(isInt8)
            "qa" -> QATask(isInt8)
            else -> throw IllegalArgumentException("Unknown task: ${spec.task}")
        }
        task.init(context)

        try {
            // 5. Warm-up iterations (20)
            for (i in 0 until config.warmupIterations) {
                val inputIdx = i % 50
                val t0 = SystemClock.elapsedRealtimeNanos()
                val pre = task.preprocess(context, inputIdx)
                val t1 = SystemClock.elapsedRealtimeNanos()
                val out = task.runInference(interpreter, pre)
                val t2 = SystemClock.elapsedRealtimeNanos()
                val res = task.postprocess(out)
                val t3 = SystemClock.elapsedRealtimeNanos()

                val nativeNanos = interpreter.lastNativeInferenceDurationNanoseconds
                val nativeMs = if (nativeNanos > 0) nativeNanos / 1e6 else (t2 - t1) / 1e6

                exporter.addRecord(
                    BenchmarkRecord(
                        session = config.session,
                        runId = runId,
                        phase = "warmup",
                        iteration = i,
                        inputIndex = inputIdx,
                        status = "ok",
                        preprocessMs = (t1 - t0) / 1e6,
                        inferenceMs = (t2 - t1) / 1e6,
                        inferenceNativeMs = nativeMs,
                        postprocessMs = (t3 - t2) / 1e6,
                        endToEndMs = (t3 - t0) / 1e6,
                        modelLoadMs = if (i == 0) modelLoadMs else null,
                        outputDigest = res
                    )
                )
            }

            // 6. Measured iterations (100)
            for (i in 0 until config.measureIterations) {
                val inputIdx = i % 50
                val t0 = SystemClock.elapsedRealtimeNanos()
                val pre = task.preprocess(context, inputIdx)
                val t1 = SystemClock.elapsedRealtimeNanos()
                val out = task.runInference(interpreter, pre)
                val t2 = SystemClock.elapsedRealtimeNanos()
                val res = task.postprocess(out)
                val t3 = SystemClock.elapsedRealtimeNanos()

                val nativeNanos = interpreter.lastNativeInferenceDurationNanoseconds
                val nativeMs = if (nativeNanos > 0) nativeNanos / 1e6 else (t2 - t1) / 1e6

                val pssMb = SystemMetrics.getPssMb(context)
                val cpuPct = SystemMetrics.sampleCpuDelta()
                val thermalStatus = SystemMetrics.getThermalStatus(context)

                exporter.addRecord(
                    BenchmarkRecord(
                        session = config.session,
                        runId = runId,
                        phase = "measure",
                        iteration = i,
                        inputIndex = inputIdx,
                        status = "ok",
                        preprocessMs = (t1 - t0) / 1e6,
                        inferenceMs = (t2 - t1) / 1e6,
                        inferenceNativeMs = nativeMs,
                        postprocessMs = (t3 - t2) / 1e6,
                        endToEndMs = (t3 - t0) / 1e6,
                        pssMb = pssMb,
                        cpuPct = cpuPct,
                        thermalStatus = thermalStatus,
                        outputDigest = res
                    )
                )
            }

            onLog("[DONE] Finished ${config.modelId} (${config.precision}, ${config.delegate})")
        } catch (e: Throwable) {
            val err = "Inference execution failed: ${e.message}"
            onLog("[ERROR] $err")
            exporter.addRecord(
                BenchmarkRecord(
                    session = config.session,
                    runId = runId,
                    phase = "measure",
                    iteration = null,
                    inputIndex = null,
                    status = "error",
                    errorMessage = err
                )
            )
        } finally {
            interpreter.close()
            gpuDelegate?.close()
            nnapiDelegate?.close()
        }

        val resultFile = exporter.flushToFile()
        onLog("[EXPORT] Saved results to: ${resultFile.name}")

        // 7. Inter-configuration cooldown (contract §2)
        if (config.cooldownSeconds > 0) {
            onLog("[COOLDOWN] Cooling down for ${config.cooldownSeconds}s...")
            Thread.sleep(config.cooldownSeconds * 1000L)
        }

        return resultFile
    }

    private fun loadModelFile(context: Context, modelAssetPath: String): ByteBuffer {
        val afd = context.assets.openFd(modelAssetPath)
        val inputStream = afd.createInputStream()
        val fileChannel = inputStream.channel
        val startOffset = afd.startOffset
        val declaredLength = afd.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength).apply {
            order(ByteOrder.nativeOrder())
        }
    }
}

