import 'package:flutter/material.dart';
import 'src/ui/benchmark_page.dart';

void main(List<String> args) {
  WidgetsFlutterBinding.ensureInitialized();

  int session = 1;
  bool autorun = false;

  for (final arg in args) {
    if (arg.startsWith('--session=')) {
      session = int.tryParse(arg.split('=')[1]) ?? 1;
    } else if (arg == '--autorun') {
      autorun = true;
    }
  }

  runApp(BenchmarkApp(session: session, autorun: autorun));
}

class BenchmarkApp extends StatelessWidget {
  final int session;
  final bool autorun;

  const BenchmarkApp({
    super.key,
    required this.session,
    required this.autorun,
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
      home: BenchmarkPage(session: session, autorun: autorun),
    );
  }
}

