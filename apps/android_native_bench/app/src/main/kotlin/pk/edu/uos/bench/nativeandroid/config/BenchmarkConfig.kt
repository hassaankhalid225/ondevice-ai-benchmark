package pk.edu.uos.bench.nativeandroid.config

import android.content.Context
import java.io.InputStream
import java.security.MessageDigest

data class ModelSpec(
    val id: String,
    val task: String,
    val fp32File: String,
    val fp32Sha256: String,
    val int8File: String,
    val int8Sha256: String
)

data class BenchmarkConfig(
    val platform: String = "android_native",
    val modelId: String,
    val precision: String, // "fp32" | "int8"
    val delegate: String,  // "cpu" | "gpu" | "nnapi"
    val threads: Int = 4,
    val warmupIterations: Int = 20,
    val measureIterations: Int = 100,
    val cooldownSeconds: Int = 60,
    val session: Int = 1
)

object BenchmarkRegistry {
    const val PROTOCOL_VERSION = "0.3.0"
    const val SCHEMA_VERSION = "1.1"

    val MODELS = listOf(
        ModelSpec(
            id = "mobilenetv3_large",
            task = "classification",
            fp32File = "models/mobilenetv3_large_fp32.tflite",
            fp32Sha256 = "f924c190e9112c7db6630ab522c8fb2972be408180d2d72b8038e1a2340b2266",
            int8File = "models/mobilenetv3_large_int8.tflite",
            int8Sha256 = "1d76f35adb879b2cde9fe39000ede3d36e6d317027799c6d0927570a22c1e8d1"
        ),
        ModelSpec(
            id = "efficientdet_lite0",
            task = "detection",
            fp32File = "models/efficientdet_lite0_fp32.tflite",
            fp32Sha256 = "70ae8c44c4e00b62c53557405e40c719632a503dbd49703df2bf30da96bf43ab",
            int8File = "models/efficientdet_lite0_int8.tflite",
            int8Sha256 = "70c5d02357c568d512d76125eef7d687f58a1a9514c301fd25b22675fc910c95"
        ),
        ModelSpec(
            id = "mobilebert_qa",
            task = "qa",
            fp32File = "models/mobilebert_qa_fp32.tflite",
            fp32Sha256 = "10358b8795d14a18c5fc4ba1eebe11fd4331109b155cca9bf013877d1b2cfa60",
            int8File = "models/mobilebert_qa_int8.tflite",
            int8Sha256 = "79471b95588d440ee959f19b275667187dc134ee2be426c30f34ea02972360f7"
        )
    )

    fun getModelSpec(modelId: String): ModelSpec {
        return MODELS.firstOrNull { it.id == modelId }
            ?: throw IllegalArgumentException("Unknown model id: $modelId")
    }

    fun verifyAssetSha256(context: Context, assetPath: String, expectedSha256: String): Boolean {
        return try {
            val digest = MessageDigest.getInstance("SHA-256")
            context.assets.open(assetPath).use { input ->
                val buffer = ByteArray(65536)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    digest.update(buffer, 0, bytesRead)
                }
            }
            val hash = digest.digest().joinToString("") { "%02x".format(it) }
            hash.equals(expectedSha256, ignoreCase = true)
        } catch (e: Exception) {
            false
        }
    }
}
