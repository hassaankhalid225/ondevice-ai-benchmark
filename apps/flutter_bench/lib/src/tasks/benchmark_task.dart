import 'package:tflite_flutter/tflite_flutter.dart';

abstract class BenchmarkTask {
  String get taskId;
  Future<void> init();
  Future<dynamic> preprocess(int inputIndex);
  dynamic runInference(Interpreter interpreter, dynamic preprocessedInput);
  String postprocess(dynamic inferenceOutput);
}

