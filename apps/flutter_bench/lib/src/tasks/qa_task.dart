import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'benchmark_task.dart';

class QATask implements BenchmarkTask {
  final bool isInt8;
  @override
  final String taskId = 'mobilebert_qa';

  final int seqLength = 384;
  late List<Int32List> inputIds;
  late List<Int32List> inputMask;
  late List<Int32List> segmentIds;

  late dynamic startLogits;
  late dynamic endLogits;
  late Map<int, Object> outputMap;

  final List<Map<String, String>> qaEntries = [];

  QATask({required this.isInt8});

  @override
  Future<void> init() async {
    inputIds = [Int32List(seqLength)];
    inputMask = [Int32List(seqLength)];
    segmentIds = [Int32List(seqLength)];

    startLogits = List.generate(1, (_) => List.filled(seqLength, 0.0));
    endLogits = List.generate(1, (_) => List.filled(seqLength, 0.0));

    outputMap = {
      0: endLogits,
      1: startLogits,
    };

    final content = await rootBundle.loadString('assets/inputs/text.jsonl');
    final lines = const LineSplitter().convert(content);
    for (final line in lines) {
      if (line.trim().isNotEmpty) {
        final map = jsonDecode(line) as Map<String, dynamic>;
        qaEntries.add({
          'question': map['question'] as String? ?? '',
          'context': map['context'] as String? ?? '',
        });
      }
    }
  }

  @override
  Future<dynamic> preprocess(int inputIndex) async {
    final entry = qaEntries[inputIndex % qaEntries.length];
    final question = entry['question']!;
    final textContext = entry['context']!;

    inputIds[0].fillRange(0, seqLength, 0);
    inputMask[0].fillRange(0, seqLength, 0);
    segmentIds[0].fillRange(0, seqLength, 0);

    inputIds[0][0] = 101; // [CLS]
    inputMask[0][0] = 1;
    int ptr = 1;

    final qTokens = question.split(RegExp(r'\s+'));
    for (final tok in qTokens) {
      if (ptr < seqLength - 2) {
        inputIds[0][ptr] = (tok.hashCode & 0x7FFF) % 30000 + 1000;
        inputMask[0][ptr] = 1;
        segmentIds[0][ptr] = 0;
        ptr++;
      }
    }
    inputIds[0][ptr] = 102; // [SEP]
    inputMask[0][ptr] = 1;
    segmentIds[0][ptr] = 0;
    ptr++;

    final cTokens = textContext.split(RegExp(r'\s+'));
    for (final tok in cTokens) {
      if (ptr < seqLength - 1) {
        inputIds[0][ptr] = (tok.hashCode & 0x7FFF) % 30000 + 1000;
        inputMask[0][ptr] = 1;
        segmentIds[0][ptr] = 1;
        ptr++;
      }
    }
    inputIds[0][ptr] = 102; // [SEP]
    inputMask[0][ptr] = 1;
    segmentIds[0][ptr] = 1;

    return [inputIds, inputMask, segmentIds];
  }

  @override
  dynamic runInference(Interpreter interpreter, dynamic preprocessedInput) {
    interpreter.runForMultipleInputs(preprocessedInput as List<Object>, outputMap);
    return [startLogits, endLogits];
  }

  @override
  String postprocess(dynamic inferenceOutput) {
    final pair = inferenceOutput as List;
    final starts = (pair[0] as List)[0] as List;
    final ends = (pair[1] as List)[0] as List;

    int bestStart = 0;
    double maxStartVal = double.negativeInfinity;
    for (int i = 0; i < starts.length; i++) {
      final v = (starts[i] as num).toDouble();
      if (v > maxStartVal) {
        maxStartVal = v;
        bestStart = i;
      }
    }

    int bestEnd = bestStart;
    double maxEndVal = double.negativeInfinity;
    for (int i = bestStart; i < ends.length; i++) {
      final v = (ends[i] as num).toDouble();
      if (v > maxEndVal) {
        maxEndVal = v;
        bestEnd = i;
      }
    }

    return 'qa:$bestStart-$bestEnd';
  }
}

