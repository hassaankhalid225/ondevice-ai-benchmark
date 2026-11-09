import 'package:flutter/services.dart';

class SystemMetrics {
  static const MethodChannel _channel = MethodChannel('pk.edu.uos.bench/metrics');

  static Future<double> getPssMb() async {
    try {
      final res = await _channel.invokeMethod<double>('getPssMb');
      return res ?? 0.0;
    } catch (_) {
      return 0.0;
    }
  }

  static Future<double> getCpuPct() async {
    try {
      final res = await _channel.invokeMethod<double>('getCpuPct');
      return res ?? 0.0;
    } catch (_) {
      return 0.0;
    }
  }

  static Future<String> getThermalStatus() async {
    try {
      final res = await _channel.invokeMethod<String>('getThermalStatus');
      return res ?? 'none';
    } catch (_) {
      return 'none';
    }
  }

  static Future<int> getBatteryChargeUah() async {
    try {
      final res = await _channel.invokeMethod<int>('getBatteryChargeUah');
      return res ?? 0;
    } catch (_) {
      return 0;
    }
  }

  static Future<String> getDeviceId() async {
    try {
      final res = await _channel.invokeMethod<String>('getDeviceId');
      return res ?? 'dev-unknown-device';
    } catch (_) {
      return 'dev-unknown-device';
    }
  }

  static Future<String> getOsVersion() async {
    try {
      final res = await _channel.invokeMethod<String>('getOsVersion');
      return res ?? '14';
    } catch (_) {
      return '14';
    }
  }

  static Future<int> getApiLevel() async {
    try {
      final res = await _channel.invokeMethod<int>('getApiLevel');
      return res ?? 34;
    } catch (_) {
      return 34;
    }
  }

  static Future<Map<String, dynamic>> getIntentExtras() async {
    try {
      final res = await _channel.invokeMapMethod<String, dynamic>('getIntentExtras');
      return res ?? {};
    } catch (_) {
      return {};
    }
  }

  static Future<void> log(String message) async {
    try {
      await _channel.invokeMethod('log', {'message': message});
    } catch (_) {}
  }

  static Future<void> finish() async {
    try {
      await _channel.invokeMethod('finish');
    } catch (_) {}
  }
}

