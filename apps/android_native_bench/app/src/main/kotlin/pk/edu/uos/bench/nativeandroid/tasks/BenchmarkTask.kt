package pk.edu.uos.bench.nativeandroid.tasks

import android.content.Context
import org.tensorflow.lite.Interpreter

interface BenchmarkTask {
    val taskId: String
    fun init(context: Context)
    fun preprocess(context: Context, inputIndex: Int): Any
    fun runInference(interpreter: Interpreter, preprocessedInput: Any): Any
    fun postprocess(inferenceOutput: Any): String
}
