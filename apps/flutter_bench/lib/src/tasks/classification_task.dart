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

  late Float32List _floatInput;
  late Int8List _int8Input;
  late Uint8List _inputBytes;
  late dynamic outputBuffer;

  ClassificationTask({required this.isInt8});

  @override
  Future<void> init() async {
    final totalElements = 1 * inputSize * inputSize * 3;
    if (isInt8) {
      _int8Input = Int8List(totalElements);
      _inputBytes = _int8Input.buffer.asUint8List();
      outputBuffer = List.generate(1, (_) => List.filled(numClasses, 0));
    } else {
      _floatInput = Float32List(totalElements);
      _inputBytes = _floatInput.buffer.asUint8List();
      outputBuffer = List.generate(1, (_) => List.filled(numClasses, 0.0));
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

    int idx = 0;
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = resized.getPixel(x, y);
        final r = pixel.r.toInt();
        final g = pixel.g.toInt();
        final b = pixel.b.toInt();

        if (isInt8) {
          _int8Input[idx] = r - 128;
          _int8Input[idx + 1] = g - 128;
          _int8Input[idx + 2] = b - 128;
        } else {
          _floatInput[idx] = r / 255.0;
          _floatInput[idx + 1] = g / 255.0;
          _floatInput[idx + 2] = b / 255.0;
        }
        idx += 3;
      }
    }
    return _inputBytes;
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
      final list = (inferenceOutput as List)[0] as List;
      int maxVal = -129;
      for (int i = 0; i < list.length; i++) {
        final val = (list[i] as num).toInt();
        if (val > maxVal) {
          maxVal = val;
          maxIdx = i;
        }
      }
    } else {
      final list = (inferenceOutput as List)[0] as List;
      double maxVal = double.negativeInfinity;
      for (int i = 0; i < list.length; i++) {
        final val = (list[i] as num).toDouble();
        if (val > maxVal) {
          maxVal = val;
          maxIdx = i;
        }
      }
    }
    return 'cls:$maxIdx';
  }
}

