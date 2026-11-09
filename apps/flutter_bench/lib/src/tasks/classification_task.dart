import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img_lib;
import 'package:tflite_flutter/tflite_flutter.dart';
import 'benchmark_task.dart';

class ClassificationTask implements BenchmarkTask {
  final bool isInt8;
  @override
  final String taskId = 'mobilenetv3_large';

  final int inputSize = 224;
  final int numClasses = 1001;

  late dynamic inputBuffer;
  late dynamic outputBuffer;

  ClassificationTask({required this.isInt8});

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
      outputBuffer = List.generate(1, (_) => Int8List(numClasses));
    } else {
      inputBuffer = List.generate(
        1,
        (_) => List.generate(
          inputSize,
          (_) => List.generate(inputSize, (_) => Float32List(3)),
        ),
      );
      outputBuffer = List.generate(1, (_) => Float32List(numClasses));
    }
  }

  @override
  Future<dynamic> preprocess(int inputIndex) async {
    final fileName = 'assets/inputs/vision/input_${(inputIndex % 50).toString().padLeft(2, '0')}.jpg';
    final byteData = await rootBundle.load(fileName);
    final rawBytes = byteData.buffer.asUint8List();

    // Pure Dart image decode & bilinear resize per contract §3
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
    interpreter.run(preprocessedInput, outputBuffer);
    return outputBuffer;
  }

  @override
  String postprocess(dynamic inferenceOutput) {
    int maxIdx = 0;
    if (isInt8) {
      final list = (inferenceOutput as List)[0] as List<int>;
      int maxVal = -129;
      for (int i = 0; i < list.length; i++) {
        if (list[i] > maxVal) {
          maxVal = list[i];
          maxIdx = i;
        }
      }
    } else {
      final list = (inferenceOutput as List)[0] as List<double>;
      double maxVal = double.negativeInfinity;
      for (int i = 0; i < list.length; i++) {
        if (list[i] > maxVal) {
          maxVal = list[i];
          maxIdx = i;
        }
      }
    }
    return 'cls:$maxIdx';
  }
}
