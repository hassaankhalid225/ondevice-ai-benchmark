package pk.edu.uos.bench.nativeandroid.ui

import android.content.Context
import android.os.Bundle
import android.os.PowerManager
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import pk.edu.uos.bench.nativeandroid.config.BenchmarkConfig
import pk.edu.uos.bench.nativeandroid.config.BenchmarkRegistry
import pk.edu.uos.bench.nativeandroid.databinding.ActivityMainBinding
import pk.edu.uos.bench.nativeandroid.harness.BenchmarkRunner
import java.util.Random

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private var wakeLock: PowerManager.WakeLock? = null
    private val scope = CoroutineScope(Dispatchers.Main)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Keep screen on during benchmark execution
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "bench:wakelock").apply {
            acquire(60 * 60 * 1000L) // 1 hour max
        }

        val session = intent.getIntExtra("session", 1)
        val autorun = intent.getBooleanExtra("autorun", false)

        binding.btnStart.setOnClickListener {
            startBenchmarkSuite(session)
        }

        if (autorun) {
            startBenchmarkSuite(session)
        }
    }

    private fun startBenchmarkSuite(session: Int) {
        binding.btnStart.isEnabled = false
        binding.tvStatus.text = "Status: Running Session $session..."

        scope.launch(Dispatchers.IO) {
            val runner = BenchmarkRunner(applicationContext) { logLine ->
                android.util.Log.i("BENCH", logLine)
                scope.launch(Dispatchers.Main) {
                    binding.tvDetails.append("$logLine\n")
                }
            }

            // Build all experimental configurations
            val configs = mutableListOf<BenchmarkConfig>()
            val models = listOf("mobilenetv3_large", "efficientdet_lite0", "mobilebert_qa")
            val precisions = listOf("fp32", "int8")
            val delegates = listOf("cpu", "gpu", "nnapi")

            for (m in models) {
                for (p in precisions) {
                    for (d in delegates) {
                        configs.add(
                            BenchmarkConfig(
                                modelId = m,
                                precision = p,
                                delegate = d,
                                session = session,
                                cooldownSeconds = 60
                            )
                        )
                    }
                }
            }

            // Seeded shuffle per contract §2: seed = 20261109 + session
            val rng = Random(20261109L + session)
            configs.shuffle(rng)

            for (cfg in configs) {
                withContext(Dispatchers.Main) {
                    binding.tvStatus.text = "Running: ${cfg.modelId} (${cfg.precision}, ${cfg.delegate})"
                }
                try {
                    runner.runConfiguration(cfg)
                } catch (e: Exception) {
                    android.util.Log.e("BENCH", "Configuration failed: ${cfg.modelId} (${cfg.precision}, ${cfg.delegate}): ${e.message}", e)
                }
            }

            withContext(Dispatchers.Main) {
                val completionMsg = "Status: Session $session Completed!"
                android.util.Log.i("BENCH", completionMsg)
                binding.tvStatus.text = completionMsg
                binding.btnStart.isEnabled = true
                if (intent.getBooleanExtra("autorun", false)) {
                    finish()
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (wakeLock?.isHeld == true) {
            wakeLock?.release()
        }
    }
}

