import 'dart:math';
import 'package:flutter/material.dart';
import '../config/benchmark_config.dart';
import '../harness/benchmark_runner.dart';

class BenchmarkPage extends StatefulWidget {
  final int session;
  final bool autorun;

  const BenchmarkPage({
    super.key,
    this.session = 1,
    this.autorun = false,
  });

  @override
  State<BenchmarkPage> createState() => _BenchmarkPageState();
}

class _BenchmarkPageState extends State<BenchmarkPage> {
  String status = 'Status: Idle';
  final StringBuffer logs = StringBuffer('Ready to execute Flutter benchmark sessions.\n');
  bool isRunning = false;

  @override
  void initState() {
    super.initState();
    if (widget.autorun) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        startBenchmarkSuite(widget.session);
      });
    }
  }

  void appendLog(String line) {
    setState(() {
      logs.writeln(line);
    });
  }

  Future<void> startBenchmarkSuite(int session) async {
    if (isRunning) return;
    setState(() {
      isRunning = true;
      status = 'Status: Running Session $session...';
    });

    final runner = BenchmarkRunner(onLog: appendLog);

    final configs = <BenchmarkConfig>[];
    const models = ['mobilenetv3_large', 'efficientdet_lite0', 'mobilebert_qa'];
    const precisions = ['fp32', 'int8'];
    const delegates = ['cpu', 'gpu', 'nnapi'];

    for (final m in models) {
      for (final p in precisions) {
        for (final d in delegates) {
          configs.add(
            BenchmarkConfig(
              modelId: m,
              precision: p,
              delegate: d,
              session: session,
              cooldownSeconds: 60,
            ),
          );
        }
      }
    }

    // Seeded shuffle per contract §2: seed = 20261109 + session
    final rng = Random(20261109 + session);
    configs.shuffle(rng);

    for (final cfg in configs) {
      setState(() {
        status = 'Running: ${cfg.modelId} (${cfg.precision}, ${cfg.delegate})';
      });
      await runner.runConfiguration(cfg);
    }

    setState(() {
      status = 'Status: Session $session Completed!';
      isRunning = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter Benchmark'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Text(
              'Flutter On-Device AI Benchmark',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              status,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 24),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(
                  child: Text(
                    logs.toString(),
                    style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: isRunning ? null : () => startBenchmarkSuite(widget.session),
                child: const Text('Start Benchmark'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

