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

  late dynamic inputBuffer;
  late Map<int, Object> outputMap;

  final outputBoxes = List.generate(
    1,
    (_) => List.generate(10, (_) => Float32List(4)),
  );
  final outputClasses = List.generate(1, (_) => Float32List(10));
  final outputScores = List.generate(1, (_) => Float32List(10));
  final numDetections = Float32List(1);

  DetectionTask({required this.isInt8});

  @override
  Future<void> init() async {
    if (isInt8) {
      inputBuffer = List.generate(
        1,
        (_) => List.generate(
          inputSize,
          (_) => List.generate(inputSize, (_) => Int8List(3)),
        ),
      );
    } else {
      inputBuffer = List.generate(
        1,
        (_) => List.generate(
          inputSize,
          (_) => List.generate(inputSize, (_) => Float32List(3)),
        ),
      );
    }
    outputMap = {
      0: outputBoxes,
      1: outputClasses,
      2: outputScores,
      3: numDetections,
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

    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = resized.getPixel(x, y);
        final r = pixel.r.toInt();
        final g = pixel.g.toInt();
        final b = pixel.b.toInt();

        if (isInt8) {
          inputBuffer[0][y][x][0] = r - 128;
          inputBuffer[0][y][x][1] = g - 128;
          inputBuffer[0][y][x][2] = b - 128;
        } else {
          inputBuffer[0][y][x][0] = r / 255.0;
          inputBuffer[0][y][x][1] = g / 255.0;
          inputBuffer[0][y][x][2] = b / 255.0;
        }
      }
    }
    return inputBuffer;
  }

  @override
  dynamic runInference(Interpreter interpreter, dynamic preprocessedInput) {
    interpreter.runForMultipleInputs([preprocessedInput], outputMap);
    return outputScores;
  }

  @override
  String postprocess(dynamic inferenceOutput) {
    final scores = (inferenceOutput as List)[0] as List<double>;
    int count = 0;
    for (final s in scores) {
      if (s >= 0.5) {
        count++;
      }
    }
    return 'det:$count';
  }
}
