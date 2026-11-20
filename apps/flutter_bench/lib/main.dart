import 'package:flutter/material.dart';
import 'src/ui/benchmark_page.dart';

void main(List<String> args) {
  WidgetsFlutterBinding.ensureInitialized();

  int session = 1;
  bool autorun = false;
  int threads = 4;
  bool cpuOnly = false;
  String loader = 'asset';

  for (final arg in args) {
    if (arg.startsWith('--session=')) {
      session = int.tryParse(arg.split('=')[1]) ?? 1;
    } else if (arg == '--autorun') {
      autorun = true;
    } else if (arg.startsWith('--threads=')) {
      threads = (int.tryParse(arg.split('=')[1]) ?? 4).clamp(1, 16);
    } else if (arg == '--cpu-only') {
      cpuOnly = true;
    } else if (arg.startsWith('--loader=')) {
      final val = arg.split('=')[1];
      if (val == 'asset' || val == 'file') {
        loader = val;
      }
    }
  }

  runApp(BenchmarkApp(
    session: session,
    autorun: autorun,
    threads: threads,
    cpuOnly: cpuOnly,
    loader: loader,
  ));
}

class BenchmarkApp extends StatelessWidget {
  final int session;
  final bool autorun;
  final int threads;
  final bool cpuOnly;
  final String loader;

  const BenchmarkApp({
    super.key,
    required this.session,
    required this.autorun,
    this.threads = 4,
    this.cpuOnly = false,
    this.loader = 'asset',
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Benchmark',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: BenchmarkPage(
        session: session,
        autorun: autorun,
        threads: threads,
        cpuOnly: cpuOnly,
        loader: loader,
      ),
    );
  }
}

