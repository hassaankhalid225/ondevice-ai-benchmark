package pk.edu.uos.bench.nativeandroid.tasks

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.nio.ByteOrder

class DetectionTask(
    private val isInt8: Boolean
) : BenchmarkTask {

    override val taskId: String = "efficientdet_lite0"

    private lateinit var inputBuffer: ByteBuffer
    private val inputSize = 320
    private val maxDetections = 10

    private val outputBoxes = Array(1) { Array(maxDetections) { FloatArray(4) } }
    private val outputClasses = Array(1) { FloatArray(maxDetections) }
    private val outputScores = Array(1) { FloatArray(maxDetections) }
    private val numDetections = FloatArray(1)
    private lateinit var outputMap: Map<Int, Any>

    override fun init(context: Context) {
        val bytesPerChannel = if (isInt8) 1 else 4
        inputBuffer = ByteBuffer.allocateDirect(1 * inputSize * inputSize * 3 * bytesPerChannel).apply {
            order(ByteOrder.nativeOrder())
        }
        outputMap = mapOf(
            0 to outputBoxes,
            1 to outputClasses,
            2 to outputScores,
            3 to numDetections
        )
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
        val inputArray = arrayOf<Any>(inBuf)
        interpreter.runForMultipleInputsOutputs(inputArray, outputMap)
        return outputScores
    }

    override fun postprocess(inferenceOutput: Any): String {
        @Suppress("UNCHECKED_CAST")
        val scores = (inferenceOutput as Array<FloatArray>)[0]
        var count = 0
        for (s in scores) {
            if (s >= 0.5f) {
                count++
            }
        }
        return "det:$count"
    }
}
