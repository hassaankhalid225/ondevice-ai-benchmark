import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../config/benchmark_config.dart';
import '../metrics/system_metrics.dart';

class BenchmarkRecord {
  final int session;
  final String runId;
  final String phase;
  final int? iteration;
  final int? inputIndex;
  final String status;
  final String? errorMessage;
  final double? preprocessMs;
  final double? inferenceMs;
  final double? inferenceNativeMs;
  final double? postprocessMs;
  final double? endToEndMs;
  final double? coldStartMs;
  final double? modelLoadMs;
  final double? pssMb;
  final double? cpuPct;
  final String thermalStatus;
  final String? outputDigest;

  BenchmarkRecord({
    required this.session,
    required this.runId,
    required this.phase,
    this.iteration,
    this.inputIndex,
    this.status = 'ok',
    this.errorMessage,
    this.preprocessMs,
    this.inferenceMs,
    this.inferenceNativeMs,
    this.postprocessMs,
    this.endToEndMs,
    this.coldStartMs,
    this.modelLoadMs,
    this.pssMb,
    this.cpuPct,
    this.thermalStatus = 'none',
    this.outputDigest,
  });
}

class JsonlExporter {
  final BenchmarkConfig config;
  final List<BenchmarkRecord> _records = [];

  JsonlExporter({required this.config});

  void addRecord(BenchmarkRecord record) {
    _records.add(record);
  }

  Future<File> flushToFile() async {
    final now = DateTime.now().toUtc();
    final yyyymmdd = "${now.year}${now.month.toString().padLeft(2, '0')}${now.day.toString().padLeft(2, '0')}";
    final sessionPad = config.session.toString().padLeft(2, '0');
    final fileName = "${yyyymmdd}_${config.platform}_${config.modelId}_${config.precision}_${config.delegate}_s$sessionPad.jsonl";

    final extDir = await getExternalStorageDirectory() ?? await getApplicationDocumentsDirectory();
    final resultsDir = Directory('${extDir.path}/results');
    if (!await resultsDir.exists()) {
      await resultsDir.create(recursive: true);
    }
    final file = File('${resultsDir.path}/$fileName');

    final deviceId = await SystemMetrics.getDeviceId();
    final osVersion = await SystemMetrics.getOsVersion();
    final apiLevel = await SystemMetrics.getApiLevel();

    final sink = file.openWrite(mode: FileMode.append);

    for (final r in _records) {
      final map = <String, dynamic>{
        'schema_version': BenchmarkRegistry.schemaVersion,
        'protocol_version': BenchmarkRegistry.protocolVersion,
        'synthetic': false,
        'timestamp_utc': now.toIso8601String(),
        'device_id': deviceId,
        'os': 'android',
        'os_version': osVersion,
        'api_level': apiLevel,
        'app_version': '1.0.0',
        'build_mode': 'release',
        'platform': config.platform,
        'runtime': 'litert',
        'runtime_version': '2.16.1',
        'model_id': config.modelId,
        'precision': config.precision,
        'delegate': config.delegate,
        'cpu_threads': config.threads,
        'session': r.session,
        'run_id': r.runId,
        'phase': r.phase,
      };

      if (r.iteration != null) map['iteration'] = r.iteration;
      if (r.inputIndex != null) map['input_index'] = r.inputIndex;
      map['status'] = r.status;
      if (r.errorMessage != null) map['error_message'] = r.errorMessage;

      if (r.preprocessMs != null) map['preprocess_ms'] = _round3(r.preprocessMs!);
      if (r.inferenceMs != null) map['inference_ms'] = _round3(r.inferenceMs!);
      if (r.inferenceNativeMs != null) map['inference_native_ms'] = _round3(r.inferenceNativeMs!);
      if (r.postprocessMs != null) map['postprocess_ms'] = _round3(r.postprocessMs!);
      if (r.endToEndMs != null) map['end_to_end_ms'] = _round3(r.endToEndMs!);

      if (r.coldStartMs != null) map['cold_start_ms'] = _round3(r.coldStartMs!);
      if (r.modelLoadMs != null) map['model_load_ms'] = _round3(r.modelLoadMs!);
      if (r.pssMb != null) map['pss_mb'] = _round2(r.pssMb!);
      if (r.cpuPct != null) map['cpu_pct'] = _round2(r.cpuPct!);
      map['thermal_status'] = r.thermalStatus;
      if (r.outputDigest != null) map['output_digest'] = r.outputDigest;

      sink.writeln(jsonEncode(map));
    }

    await sink.flush();
    await sink.close();
    _records.clear();
    return file;
  }

  double _round3(double v) => (v * 1000).round() / 1000;
  double _round2(double v) => (v * 100).round() / 100;
}

