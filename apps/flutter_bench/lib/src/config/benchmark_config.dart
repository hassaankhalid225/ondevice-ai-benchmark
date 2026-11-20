import 'package:crypto/crypto.dart';
import 'package:flutter/services.dart';

class ModelSpec {
  final String id;
  final String task;
  final String fp32File;
  final String fp32Sha256;
  final String int8File;
  final String int8Sha256;

  const ModelSpec({
    required this.id,
    required this.task,
    required this.fp32File,
    required this.fp32Sha256,
    required this.int8File,
    required this.int8Sha256,
  });
}

class BenchmarkConfig {
  final String platform;
  final String modelId;
  final String precision; // 'fp32' | 'int8'
  final String delegate;  // 'cpu' | 'gpu' | 'nnapi'
  final String loader;    // 'asset' (fromBuffer calloc) | 'file' (fromFile mmap)
  final int threads;
  final int warmupIterations;
  final int measureIterations;
  final int cooldownSeconds;
  final int session;

  const BenchmarkConfig({
    this.platform = 'flutter',
    required this.modelId,
    required this.precision,
    required this.delegate,
    this.loader = 'asset',
    this.threads = 4,
    this.warmupIterations = 20,
    this.measureIterations = 100,
    this.cooldownSeconds = 60,
    this.session = 1,
  });
}

class BenchmarkRegistry {
  static const String protocolVersion = '0.3.0';
  static const String schemaVersion = '1.1';

  static const List<ModelSpec> models = [
    ModelSpec(
      id: 'mobilenetv3_large',
      task: 'classification',
      fp32File: 'assets/models/mobilenetv3_large_fp32.tflite',
      fp32Sha256: 'f924c190e9112c7db6630ab522c8fb2972be408180d2d72b8038e1a2340b2266',
      int8File: 'assets/models/mobilenetv3_large_int8.tflite',
      int8Sha256: '1d76f35adb879b2cde9fe39000ede3d36e6d317027799c6d0927570a22c1e8d1',
    ),
    ModelSpec(
      id: 'efficientdet_lite0',
      task: 'detection',
      fp32File: 'assets/models/efficientdet_lite0_fp32.tflite',
      fp32Sha256: '70ae8c44c4e00b62c53557405e40c719632a503dbd49703df2bf30da96bf43ab',
      int8File: 'assets/models/efficientdet_lite0_int8.tflite',
      int8Sha256: '70c5d02357c568d512d76125eef7d687f58a1a9514c301fd25b22675fc910c95',
    ),
    ModelSpec(
      id: 'mobilebert_qa',
      task: 'qa',
      fp32File: 'assets/models/mobilebert_qa_fp32.tflite',
      fp32Sha256: '10358b8795d14a18c5fc4ba1eebe11fd4331109b155cca9bf013877d1b2cfa60',
      int8File: 'assets/models/mobilebert_qa_int8.tflite',
      int8Sha256: '79471b95588d440ee959f19b275667187dc134ee2be426c30f34ea02972360f7',
    ),
  ];

  static ModelSpec getModelSpec(String modelId) {
    return models.firstWhere(
      (m) => m.id == modelId,
      orElse: () => throw ArgumentError('Unknown model id: $modelId'),
    );
  }

  static Future<bool> verifyAssetSha256(String assetPath, String expectedSha256) async {
    try {
      final byteData = await rootBundle.load(assetPath);
      final bytes = byteData.buffer.asUint8List();
      final digest = sha256.convert(bytes);
      return digest.toString().toLowerCase() == expectedSha256.toLowerCase();
    } catch (_) {
      return false;
    }
  }
}
