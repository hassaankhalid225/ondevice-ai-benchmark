import 'dart:io';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import '../config/benchmark_config.dart';
import '../harness/benchmark_runner.dart';
import '../metrics/system_metrics.dart';

class BenchmarkPage extends StatefulWidget {
  final int session;
  final bool autorun;
  final int threads;
  final bool cpuOnly;
  final String loader;

  const BenchmarkPage({
    super.key,
    this.session = 1,
    this.autorun = false,
    this.threads = 4,
    this.cpuOnly = false,
    this.loader = 'asset',
  });

  @override
  State<BenchmarkPage> createState() => _BenchmarkPageState();
}

class _BenchmarkPageState extends State<BenchmarkPage> {
  String status = 'Status: Idle';
  final StringBuffer logs = StringBuffer('Ready to execute Flutter benchmark sessions.\n');
  bool isRunning = false;
  late int selectedThreads;
  late bool cpuOnlyMode;
  late String selectedLoader;

  @override
  void initState() {
    super.initState();
    selectedThreads = widget.threads;
    cpuOnlyMode = widget.cpuOnly;
    selectedLoader = widget.loader;
    _checkIntentAndAutorun();
  }

  Future<void> _checkIntentAndAutorun() async {
    final extras = await SystemMetrics.getIntentExtras();
    final intentSession = extras['session'] as int? ?? widget.session;
    final intentAutorun = extras['autorun'] as bool? ?? widget.autorun;
    final intentThreads = (extras['threads'] as int? ?? widget.threads).clamp(1, 16);
    final intentCpuOnly = extras['cpuOnly'] as bool? ?? widget.cpuOnly;
    final rawLoader = extras['loader'] as String? ?? widget.loader;
    final intentLoader = (rawLoader == 'asset' || rawLoader == 'file') ? rawLoader : 'asset';

    setState(() {
      selectedThreads = intentThreads;
      cpuOnlyMode = intentCpuOnly;
      selectedLoader = intentLoader;
    });

    if (intentAutorun) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        startBenchmarkSuite(
          intentSession,
          threads: intentThreads,
          cpuOnly: intentCpuOnly,
          loader: intentLoader,
          autoFinish: true,
        );
      });
    }
  }

  Future<void> _clearExistingSessionFiles(int session) async {
    final extDir = await getExternalStorageDirectory() ?? await getApplicationDocumentsDirectory();
    final resultsDir = Directory('${extDir.path}/results');
    if (!await resultsDir.exists()) return;
    final suffix = '_s${session.toString().padLeft(2, '0')}.jsonl';
    await for (final entity in resultsDir.list()) {
      if (entity is File && entity.path.endsWith(suffix)) {
        await entity.delete();
      }
    }
  }

  void appendLog(String line) {
    SystemMetrics.log(line);
    setState(() {
      logs.writeln(line);
    });
  }

  Future<void> startBenchmarkSuite(
    int session, {
    int? threads,
    bool? cpuOnly,
    String? loader,
    bool autoFinish = false,
  }) async {
    if (isRunning) return;
    final activeThreads = (threads ?? selectedThreads).clamp(1, 16);
    final activeCpuOnly = cpuOnly ?? cpuOnlyMode;
    final activeLoader = loader ?? selectedLoader;

    setState(() {
      isRunning = true;
      status = 'Status: Running Session $session (${activeCpuOnly ? "cpuOnly" : "full"}, ${activeThreads}t, $activeLoader)...';
    });

    await _clearExistingSessionFiles(session);
    final runner = BenchmarkRunner(onLog: appendLog);

    final configs = <BenchmarkConfig>[];
    const models = ['mobilenetv3_large', 'efficientdet_lite0', 'mobilebert_qa'];
    const precisions = ['fp32', 'int8'];
    final delegates = activeCpuOnly ? ['cpu'] : ['cpu', 'gpu', 'nnapi'];

    for (final m in models) {
      for (final p in precisions) {
        for (final d in delegates) {
          configs.add(
            BenchmarkConfig(
              modelId: m,
              precision: p,
              delegate: d,
              loader: activeLoader,
              threads: activeThreads,
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
        status = 'Running: ${cfg.modelId} (${cfg.precision}, ${cfg.delegate}, ${cfg.threads}t)';
      });
      try {
        await runner.runConfiguration(cfg);
      } catch (e) {
        appendLog('[ERROR] Configuration failed: ${cfg.modelId} (${cfg.precision}, ${cfg.delegate}): $e');
      }
    }

    final completionMsg = 'Status: Session $session Completed!';
    appendLog(completionMsg);
    setState(() {
      status = completionMsg;
      isRunning = false;
    });

    if (autoFinish) {
      await SystemMetrics.finish();
    }
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
            const SizedBox(height: 8),
            Text(
              status,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              alignment: WrapAlignment.center,
              children: [
                ChoiceChip(
                  label: const Text('1 Thread'),
                  selected: selectedThreads == 1,
                  onSelected: isRunning ? null : (_) => setState(() => selectedThreads = 1),
                ),
                ChoiceChip(
                  label: const Text('4 Threads'),
                  selected: selectedThreads == 4,
                  onSelected: isRunning ? null : (_) => setState(() => selectedThreads = 4),
                ),
                FilterChip(
                  label: const Text('CPU Only'),
                  selected: cpuOnlyMode,
                  onSelected: isRunning ? null : (v) => setState(() => cpuOnlyMode = v),
                ),
                ChoiceChip(
                  label: const Text('fromAsset'),
                  selected: selectedLoader == 'asset',
                  onSelected: isRunning ? null : (_) => setState(() => selectedLoader = 'asset'),
                ),
                ChoiceChip(
                  label: const Text('fromFile (mmap)'),
                  selected: selectedLoader == 'file',
                  onSelected: isRunning ? null : (_) => setState(() => selectedLoader = 'file'),
                ),
              ],
            ),
            const SizedBox(height: 16),
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

