import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img_lib;
import 'package:tflite_flutter/tflite_flutter.dart';
import 'benchmark_task.dart';

class DetectionTask implements BenchmarkTask {
  final bool isInt8;
  @override
  final String taskId = 'efficientdet_lite0';

  final int inputSize = 320;
  final int maxDetections = 10;

  late Float32List _floatInput;
  late Uint8List _inputBytes;
  late Map<int, Object> outputMap;

  final outputBoxes = List.generate(
    1,
    (_) => List.generate(10, (_) => List.filled(4, 0.0)),
  );
  final outputClasses = List.generate(1, (_) => List.filled(10, 0.0));
  final outputScores = List.generate(1, (_) => List.filled(10, 0.0));
  final numDetections = List.generate(1, (_) => List.filled(1, 0.0));

  DetectionTask({required this.isInt8});

  @override
  Future<void> init() async {
    final totalElements = 1 * inputSize * inputSize * 3;
    _floatInput = Float32List(totalElements);
    _inputBytes = _floatInput.buffer.asUint8List();

    outputMap = {
      0: outputScores,
      1: numDetections,
      2: outputBoxes,
      3: outputClasses,
    };
  }

  @override
  Future<dynamic> preprocess(int inputIndex) async {
    final fileName = 'assets/inputs/vision/input_${(inputIndex % 50).toString().padLeft(2, '0')}.jpg';
    final byteData = await rootBundle.load(fileName);
    final rawBytes = byteData.buffer.asUint8List();

    final decoded = img_lib.decodeImage(rawBytes)!;
    final resized = img_lib.copyResize(
      decoded,
      width: inputSize,
      height: inputSize,
      interpolation: img_lib.Interpolation.linear,
    );

    int idx = 0;
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = resized.getPixel(x, y);
        final r = pixel.r.toInt();
        final g = pixel.g.toInt();
        final b = pixel.b.toInt();

        _floatInput[idx] = r / 255.0;
        _floatInput[idx + 1] = g / 255.0;
        _floatInput[idx + 2] = b / 255.0;
        idx += 3;
      }
    }
    return _inputBytes;
  }

  @override
  dynamic runInference(Interpreter interpreter, dynamic preprocessedInput) {
    interpreter.runForMultipleInputs([preprocessedInput], outputMap);
    return outputScores;
  }

  @override
  String postprocess(dynamic inferenceOutput) {
    final scores = (inferenceOutput as List)[0] as List;
    int count = 0;
    for (final s in scores) {
      if ((s as num).toDouble() >= 0.5) {
        count++;
      }
    }
    return 'det:$count';
  }
}

