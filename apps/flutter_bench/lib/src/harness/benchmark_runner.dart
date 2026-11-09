import 'dart:io';
import 'package:tflite_flutter/tflite_flutter.dart';
import '../config/benchmark_config.dart';
import '../export/jsonl_exporter.dart';
import '../metrics/system_metrics.dart';
import '../tasks/benchmark_task.dart';
import '../tasks/classification_task.dart';
import '../tasks/detection_task.dart';
import '../tasks/qa_task.dart';

class BenchmarkRunner {
  final void Function(String)? onLog;

  BenchmarkRunner({this.onLog});

  Future<File> runConfiguration(BenchmarkConfig config) async {
    final runId = '${DateTime.now().millisecondsSinceEpoch}';
    final exporter = JsonlExporter(config: config);
    final spec = BenchmarkRegistry.getModelSpec(config.modelId);
    final isInt8 = config.precision == 'int8';
    final modelAssetPath = isInt8 ? spec.int8File : spec.fp32File;
    final expectedSha256 = isInt8 ? spec.int8Sha256 : spec.fp32Sha256;

    onLog?.call('[RUN] Starting ${config.modelId} (${config.precision}, ${config.delegate}) session ${config.session}');

    // 1. Verify model hash parity (contract §1)
    final verified = await BenchmarkRegistry.verifyAssetSha256(modelAssetPath, expectedSha256);
    if (!verified) {
      final err = 'Model SHA-256 verification failed for $modelAssetPath';
      onLog?.call('[ERROR] $err');
      exporter.addRecord(
        BenchmarkRecord(
          session: config.session,
          runId: runId,
          phase: 'measure',
          status: 'error',
          errorMessage: err,
        ),
      );
      return await exporter.flushToFile();
    }

    // 2. Wait for thermal cooldown if needed (contract §2)
    var thermal = await SystemMetrics.getThermalStatus();
    if (thermal == 'moderate' || thermal == 'severe' || thermal == 'critical') {
      onLog?.call('[THERMAL] Waiting for device cooldown (current: $thermal)...');
      var waitCount = 0;
      while ((thermal == 'moderate' || thermal == 'severe' || thermal == 'critical') && waitCount < 12) {
        await Future.delayed(const Duration(seconds: 5));
        thermal = await SystemMetrics.getThermalStatus();
        waitCount++;
      }
    }

    // 3. Delegate & Interpreter creation
    final options = InterpreterOptions()..threads = config.threads;

    try {
      if (config.delegate == 'gpu') {
        final gpuDelegate = GpuDelegateV2(
          options: GpuDelegateOptionsV2(
            isPrecisionLossAllowed: config.precision == 'fp16' || config.precision == 'int8',
          ),
        );
        options.addDelegate(gpuDelegate);
      } else if (config.delegate == 'cpu') {
        final xnnpack = XNNPackDelegate();
        options.addDelegate(xnnpack);
      } else if (config.delegate == 'nnapi') {
        const msg = 'NNAPI delegate is unsupported in tflite_flutter 0.10.4 Dart bindings';
        onLog?.call('[WARN] $msg');
        exporter.addRecord(
          BenchmarkRecord(
            session: config.session,
            runId: runId,
            phase: 'measure',
            status: 'unsupported',
            errorMessage: msg,
          ),
        );
        return await exporter.flushToFile();
      }
    } catch (e) {
      final msg = 'Delegate initialization unsupported: $e';
      onLog?.call('[WARN] $msg');
      exporter.addRecord(
        BenchmarkRecord(
          session: config.session,
          runId: runId,
          phase: 'measure',
          status: 'unsupported',
          errorMessage: msg,
        ),
      );
      return await exporter.flushToFile();
    }

    // Measure model_load_ms
    final loadSw = Stopwatch()..start();
    Interpreter interpreter;
    try {
      interpreter = await Interpreter.fromAsset(modelAssetPath, options: options);
    } catch (e) {
      final msg = 'Interpreter creation unsupported for delegate ${config.delegate}: $e';
      onLog?.call('[WARN] $msg');
      exporter.addRecord(
        BenchmarkRecord(
          session: config.session,
          runId: runId,
          phase: 'measure',
          status: 'unsupported',
          errorMessage: msg,
        ),
      );
      return await exporter.flushToFile();
    }
    loadSw.stop();
    final modelLoadMs = loadSw.elapsedMicroseconds / 1000.0;

    // 4. Initialize task
    final BenchmarkTask task;
    switch (spec.task) {
      case 'classification':
        task = ClassificationTask(isInt8: isInt8);
        break;
      case 'detection':
        task = DetectionTask(isInt8: isInt8);
        break;
      case 'qa':
        task = QATask(isInt8: isInt8);
        break;
      default:
        throw ArgumentError('Unknown task: ${spec.task}');
    }
    await task.init();

    final sw = Stopwatch();

    try {
      // 5. Warm-up iterations (20)
      for (int i = 0; i < config.warmupIterations; i++) {
        final inputIdx = i % 50;

        sw.reset();
        sw.start();
        final pre = await task.preprocess(inputIdx);
        final t1 = sw.elapsedMicroseconds;
        final out = task.runInference(interpreter, pre);
        final t2 = sw.elapsedMicroseconds;
        final res = task.postprocess(out);
        final t3 = sw.elapsedMicroseconds;
        sw.stop();

        final nativeMicros = interpreter.lastNativeInferenceDurationMicroSeconds;
        final nativeMs = nativeMicros > 0 ? nativeMicros / 1000.0 : (t2 - t1) / 1000.0;

        exporter.addRecord(
          BenchmarkRecord(
            session: config.session,
            runId: runId,
            phase: 'warmup',
            iteration: i,
            inputIndex: inputIdx,
            status: 'ok',
            preprocessMs: t1 / 1000.0,
            inferenceMs: (t2 - t1) / 1000.0,
            inferenceNativeMs: nativeMs,
            postprocessMs: (t3 - t2) / 1000.0,
            endToEndMs: t3 / 1000.0,
            modelLoadMs: i == 0 ? modelLoadMs : null,
            outputDigest: res,
          ),
        );
        await Future.delayed(Duration.zero);
      }

      // 6. Measured iterations (100)
      for (int i = 0; i < config.measureIterations; i++) {
        final inputIdx = i % 50;

        sw.reset();
        sw.start();
        final pre = await task.preprocess(inputIdx);
        final t1 = sw.elapsedMicroseconds;
        final out = task.runInference(interpreter, pre);
        final t2 = sw.elapsedMicroseconds;
        final res = task.postprocess(out);
        final t3 = sw.elapsedMicroseconds;
        sw.stop();

        final nativeMicros = interpreter.lastNativeInferenceDurationMicroSeconds;
        final nativeMs = nativeMicros > 0 ? nativeMicros / 1000.0 : (t2 - t1) / 1000.0;

        final pssMb = await SystemMetrics.getPssMb();
        final cpuPct = await SystemMetrics.getCpuPct();
        final thermalStatus = await SystemMetrics.getThermalStatus();

        exporter.addRecord(
          BenchmarkRecord(
            session: config.session,
            runId: runId,
            phase: 'measure',
            iteration: i,
            inputIndex: inputIdx,
            status: 'ok',
            preprocessMs: t1 / 1000.0,
            inferenceMs: (t2 - t1) / 1000.0,
            inferenceNativeMs: nativeMs,
            postprocessMs: (t3 - t2) / 1000.0,
            endToEndMs: t3 / 1000.0,
            pssMb: pssMb,
            cpuPct: cpuPct,
            thermalStatus: thermalStatus,
            outputDigest: res,
          ),
        );
        await Future.delayed(Duration.zero);
      }

      onLog?.call('[DONE] Finished ${config.modelId} (${config.precision}, ${config.delegate})');
    } catch (e) {
      final err = 'Inference execution failed: $e';
      onLog?.call('[ERROR] $err');
      exporter.addRecord(
        BenchmarkRecord(
          session: config.session,
          runId: runId,
          phase: 'measure',
          status: 'error',
          errorMessage: err,
        ),
      );
    } finally {
      interpreter.close();
    }

    final resultFile = await exporter.flushToFile();
    onLog?.call('[EXPORT] Saved results to: ${resultFile.path}');

    // 7. Inter-configuration cooldown
    if (config.cooldownSeconds > 0) {
      onLog?.call('[COOLDOWN] Cooling down for ${config.cooldownSeconds}s...');
      await Future.delayed(Duration(seconds: config.cooldownSeconds));
    }

    return resultFile;
  }
}
