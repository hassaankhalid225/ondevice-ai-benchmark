package pk.edu.uos.bench.nativeandroid.tasks

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.nio.ByteOrder

class ClassificationTask(
    private val isInt8: Boolean
) : BenchmarkTask {

    override val taskId: String = "mobilenetv3_large"

    private lateinit var inputBuffer: ByteBuffer
    private lateinit var outputBuffer: Any
    private val inputSize = 224
    private val numClasses = 1001

    override fun init(context: Context) {
        val bytesPerChannel = if (isInt8) 1 else 4
        inputBuffer = ByteBuffer.allocateDirect(1 * inputSize * inputSize * 3 * bytesPerChannel).apply {
            order(ByteOrder.nativeOrder())
        }
        outputBuffer = if (isInt8) {
            Array(1) { ByteArray(numClasses) }
        } else {
            Array(1) { FloatArray(numClasses) }
        }
    }

    override fun preprocess(context: Context, inputIndex: Int): Any {
        val fileName = "inputs/vision/input_%02d.jpg".format(inputIndex % 50)
        val bitmap = context.assets.open(fileName).use { stream ->
            BitmapFactory.decodeStream(stream)
        }
        val resized = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)

        inputBuffer.rewind()
        val intValues = IntArray(inputSize * inputSize)
        resized.getPixels(intValues, 0, inputSize, 0, 0, inputSize, inputSize)

        for (pixel in intValues) {
            val r = (pixel shr 16) and 0xFF
            val g = (pixel shr 8) and 0xFF
            val b = pixel and 0xFF

            if (isInt8) {
                inputBuffer.put((r - 128).toByte())
                inputBuffer.put((g - 128).toByte())
                inputBuffer.put((b - 128).toByte())
            } else {
                inputBuffer.putFloat(r / 255.0f)
                inputBuffer.putFloat(g / 255.0f)
                inputBuffer.putFloat(b / 255.0f)
            }
        }
        return inputBuffer
    }

    override fun runInference(interpreter: Interpreter, preprocessedInput: Any): Any {
        val inBuf = preprocessedInput as ByteBuffer
        inBuf.rewind()
        interpreter.run(inBuf, outputBuffer)
        return outputBuffer
    }

    override fun postprocess(inferenceOutput: Any): String {
        var maxIdx = 0
        if (isInt8) {
            @Suppress("UNCHECKED_CAST")
            val arr = (inferenceOutput as Array<ByteArray>)[0]
            var maxVal = Byte.MIN_VALUE
            for (i in arr.indices) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i]
                    maxIdx = i
                }
            }
        } else {
            @Suppress("UNCHECKED_CAST")
            val arr = (inferenceOutput as Array<FloatArray>)[0]
            var maxVal = Float.NEGATIVE_INFINITY
            for (i in arr.indices) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i]
                    maxIdx = i
                }
            }
        }
        return "cls:$maxIdx"
    }
}

