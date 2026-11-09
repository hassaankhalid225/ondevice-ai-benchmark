package pk.edu.uos.bench.nativeandroid.tasks

import android.content.Context
import org.json.JSONObject
import org.tensorflow.lite.Interpreter
import java.io.BufferedReader
import java.io.InputStreamReader

class QATask(
    private val isInt8: Boolean
) : BenchmarkTask {

    override val taskId: String = "mobilebert_qa"

    private val seqLength = 384
    private val inputIds = Array(1) { IntArray(seqLength) }
    private val inputMask = Array(1) { IntArray(seqLength) }
    private val segmentIds = Array(1) { IntArray(seqLength) }

    private val startLogits = Array(1) { FloatArray(seqLength) }
    private val endLogits = Array(1) { FloatArray(seqLength) }
    private lateinit var outputMap: Map<Int, Any>

    private val qaEntries = mutableListOf<Pair<String, String>>()

    override fun init(context: Context) {
        outputMap = mapOf(
            0 to endLogits,
            1 to startLogits
        )
        // Load text QA pairs
        context.assets.open("inputs/text.jsonl").use { stream ->
            BufferedReader(InputStreamReader(stream)).forEachLine { line ->
                if (line.isNotBlank()) {
                    val obj = JSONObject(line)
                    val q = obj.optString("question", "")
                    val c = obj.optString("context", "")
                    qaEntries.add(q to c)
                }
            }
        }
    }

    override fun preprocess(context: Context, inputIndex: Int): Any {
        val entry = qaEntries[inputIndex % qaEntries.size]
        val question = entry.first
        val textContext = entry.second

        // Deterministic subword/hash tokenization for benchmark consistency
        inputIds[0].fill(0)
        inputMask[0].fill(0)
        segmentIds[0].fill(0)

        inputIds[0][0] = 101 // [CLS]
        inputMask[0][0] = 1
        var ptr = 1

        val qTokens = question.split("\\s+".toRegex())
        for (tok in qTokens) {
            if (ptr < seqLength - 2) {
                inputIds[0][ptr] = (tok.hashCode() and 0x7FFF) % 30000 + 1000
                inputMask[0][ptr] = 1
                segmentIds[0][ptr] = 0
                ptr++
            }
        }
        inputIds[0][ptr] = 102 // [SEP]
        inputMask[0][ptr] = 1
        segmentIds[0][ptr] = 0
        ptr++

        val cTokens = textContext.split("\\s+".toRegex())
        for (tok in cTokens) {
            if (ptr < seqLength - 1) {
                inputIds[0][ptr] = (tok.hashCode() and 0x7FFF) % 30000 + 1000
                inputMask[0][ptr] = 1
                segmentIds[0][ptr] = 1
                ptr++
            }
        }
        inputIds[0][ptr] = 102 // [SEP]
        inputMask[0][ptr] = 1
        segmentIds[0][ptr] = 1

        return arrayOf(inputIds, inputMask, segmentIds)
    }

    override fun runInference(interpreter: Interpreter, preprocessedInput: Any): Any {
        @Suppress("UNCHECKED_CAST")
        val inputs = preprocessedInput as Array<Any>
        interpreter.runForMultipleInputsOutputs(inputs, outputMap)
        return Pair(startLogits, endLogits)
    }

    override fun postprocess(inferenceOutput: Any): String {
        @Suppress("UNCHECKED_CAST")
        val pair = inferenceOutput as Pair<Array<FloatArray>, Array<FloatArray>>
        val starts = pair.first[0]
        val ends = pair.second[0]

        var bestStart = 0
        var maxStartVal = Float.NEGATIVE_INFINITY
        for (i in starts.indices) {
            if (starts[i] > maxStartVal) {
                maxStartVal = starts[i]
                bestStart = i
            }
        }

        var bestEnd = bestStart
        var maxEndVal = Float.NEGATIVE_INFINITY
        for (i in bestStart until ends.size) {
            if (ends[i] > maxEndVal) {
                maxEndVal = ends[i]
                bestEnd = i
            }
        }

        return "qa:$bestStart-$bestEnd"
    }
}

