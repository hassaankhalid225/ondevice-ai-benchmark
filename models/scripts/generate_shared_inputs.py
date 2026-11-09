"""Generate standardized, deterministic shared benchmark inputs (50 vision + 50 text).

Conforms to benchmark-spec/protocol.yaml (v0.3.0) and benchmark-spec/harness-contract.md.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def generate_vision_inputs(output_dir: Path, n: int = 50, seed: int = 20261109) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    for i in range(n):
        # Create varied natural/synthetic scenes with gradients and geometric shapes
        w, h = 320, 320  # native resolution suitable for both 224x224 and 320x320 models
        # Base gradient
        c1 = rng.integers(30, 220, size=3)
        c2 = rng.integers(30, 220, size=3)
        grad = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(h):
            alpha = y / h
            grad[y, :] = (1 - alpha) * c1 + alpha * c2

        img = Image.fromarray(grad, mode="RGB")
        draw = ImageDraw.Draw(img)

        # Draw 3-6 distinct geometric objects (mimicking detection/classification scenes)
        num_shapes = int(rng.integers(3, 7))
        for _ in range(num_shapes):
            shape_type = rng.choice(["rectangle", "ellipse", "polygon"])
            x0 = int(rng.integers(10, w - 80))
            y0 = int(rng.integers(10, h - 80))
            x1 = int(x0 + rng.integers(30, 80))
            y1 = int(y0 + rng.integers(30, 80))
            fill_color = tuple(int(c) for c in rng.integers(0, 256, size=3))

            if shape_type == "rectangle":
                draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=(255, 255, 255))
            elif shape_type == "ellipse":
                draw.ellipse([x0, y0, x1, y1], fill=fill_color, outline=(0, 0, 0))
            else:
                x2 = int(rng.integers(10, w - 10))
                y2 = int(rng.integers(10, h - 10))
                draw.polygon([(x0, y0), (x1, y1), (x2, y2)], fill=fill_color)

        img_path = output_dir / f"input_{i:02d}.jpg"
        img.save(img_path, format="JPEG", quality=90)

    print(f"Generated {n} vision inputs in {output_dir}")


def generate_text_inputs(output_path: Path, n: int = 50) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 50 realistic QA pairs based on computer science, AI, systems, and mobile software
    qa_samples = [
        ("What is LiteRT?", "LiteRT is Google's high-performance runtime for on-device machine learning, formerly known as TensorFlow Lite."),
        ("What is Flutter?", "Flutter is an open-source UI software development kit created by Google for cross-platform application development."),
        ("What is ahead-of-time compilation?", "Ahead-of-time compilation converts high-level programming language code directly into native machine architecture instructions before execution."),
        ("What does XNNPACK accelerate?", "XNNPACK is an optimized library of neural network inference operators providing high performance floating-point and quantized execution on ARM and x86 CPUs."),
        ("What is NNAPI on Android?", "Android Neural Networks API is a hardware abstraction layer designed to run computationally intensive operations on machine learning hardware accelerators."),
        ("What is MobileNetV3?", "MobileNetV3 is a lightweight deep learning architecture tuned for mobile device CPUs through network search and hardware-aware optimizations."),
        ("What does post-training quantization achieve?", "Post-training quantization converts floating-point weights and activations to 8-bit integers, reducing memory footprint and accelerating inference on edge hardware."),
        ("What is the primary metric of inference latency?", "Inference latency is the elapsed duration between feeding an input tensor into the runtime interpreter and receiving the generated output tensor."),
        ("What does PSS stand for in Android memory profiling?", "Proportional Set Size measures the private memory of a process plus its proportional share of shared memory libraries across the operating system."),
        ("Why does thermal throttling occur?", "Thermal throttling reduces processor clock frequencies automatically when device temperatures exceed safety thresholds to prevent hardware overheating."),
        ("What is SQuAD?", "The Stanford Question Answering Dataset is a benchmark consisting of questions posed by crowdworkers on a collection of Wikipedia articles."),
        ("What is EfficientDet?", "EfficientDet is a family of scalable and efficient object detection models utilizing a weighted bi-directional feature pyramid network and compound scaling."),
        ("What is Dart FFI?", "Dart Foreign Function Interface allows Dart programs running in the Dart VM to allocate native memory and call C libraries directly without platform channels."),
        ("What is a platform channel in Flutter?", "A platform channel is an asynchronous communication bridge that serializes messages between Dart code and native host platform code."),
        ("What does R8 do in Android builds?", "R8 is the default code shrinker, optimizer, and dexer for Android applications that reduces app size and strips unused bytecode."),
        ("What is the purpose of warm-up iterations?", "Warm-up iterations prime runtime caches, stabilize CPU frequency governors, and compile execution kernels before measurement begins."),
        ("What is Cliff's delta?", "Cliff's delta is a non-parametric effect size metric that quantifies the degree of dominance of one distribution over another without assuming normality."),
        ("Why is the Mann-Whitney U test used?", "The Mann-Whitney U test is a non-parametric statistical hypothesis test used to assess whether values in one group tend to be larger than in another."),
        ("What does the Holm-Bonferroni method control?", "The Holm-Bonferroni method controls the family-wise error rate across multiple statistical hypothesis comparisons while providing higher statistical power than standard Bonferroni correction."),
        ("What is cold-start time in mobile apps?", "Cold-start time measures the total latency elapsed from the initial process creation by the operating system until the first frame or inference result is produced."),
        ("What is an isolate in Dart?", "An isolate is an independent execution thread in Dart with its own private heap memory, communicating with other isolates solely via message passing."),
        ("What is MobileBERT?", "MobileBERT is a compressed task-agnostic version of BERT designed specifically for resource-constrained devices via deep progressive knowledge distillation."),
        ("What is an APK file?", "An Android Package Kit is the file format used by the Android operating system for the distribution and installation of mobile applications."),
        ("What does top-1 accuracy measure?", "Top-1 accuracy measures the proportion of test examples where the highest-probability class predicted by a classification model matches the true label."),
        ("What is IoU in object detection?", "Intersection over Union measures the overlap ratio between a predicted bounding box and the ground truth annotation box in object detection."),
        ("What is WordPiece tokenization?", "WordPiece tokenization segments text into subword units based on likelihood maximization, enabling compact vocabulary coverage for out-of-vocabulary words."),
        ("What is Skia?", "Skia is an open-source 2D graphics library providing common APIs across multiple hardware and software platforms, historically used by Flutter."),
        ("What is Impeller in Flutter?", "Impeller is Flutter's modern rendering engine designed to eliminate runtime shader compilation jank by precompiling all shaders at build time."),
        ("What is a confusion matrix?", "A confusion matrix is a tabular layout that visualizes the performance of an algorithm by comparing actual target classes against predicted classes."),
        ("What does DVFS mean in mobile systems?", "Dynamic Voltage and Frequency Scaling is a power management technique where processor frequency and voltage are adjusted in real time based on workload."),
        ("What is non-maximum suppression?", "Non-maximum suppression is a postprocessing technique in object detection that filters redundant overlapping bounding boxes based on confidence scores."),
        ("What is an execution delegate in LiteRT?", "An execution delegate is a backend plugin that enables hardware-accelerated execution of supported subgraphs on GPUs, DSPs, or NPUs."),
        ("Why use release mode for benchmarks?", "Release mode disables debugging overhead, turns on Ahead-of-Time optimizations, enables compiler optimizations, and reflects real production performance."),
        ("What is bilinear interpolation?", "Bilinear interpolation is an image resampling algorithm that computes the output pixel value using the weighted average of the four nearest pixel values."),
        ("What is the ImageNet dataset?", "ImageNet is a large-scale visual database of millions of hand-annotated images designed for visual object recognition research."),
        ("What is pseudo-replication in statistics?", "Pseudo-replication is the artificial inflation of sample size by treating non-independent observations from the same experimental unit as independent replicates."),
        ("What does CPU utime represent in Linux?", "The utime metric in proc stat represents the amount of time that a process has spent executing in user mode within the processor."),
        ("What does CPU stime represent in Linux?", "The stime metric in proc stat represents the amount of time that a process has spent executing system calls inside the operating system kernel."),
        ("What is bootstrap confidence interval?", "A bootstrap confidence interval is a resampling method that estimates the variability of a statistic by repeatedly sampling with replacement from empirical data."),
        ("What is battery fuel gauge?", "A battery fuel gauge is a hardware sensing component on mobile devices that monitors battery charge, voltage, current, and accumulated energy draw."),
        ("What is INT8 quantization?", "INT8 quantization maps 32-bit floating-point numbers to signed 8-bit integers, reducing memory bandwidth requirements by four times."),
        ("What is COCO dataset?", "Common Objects in Context is a large-scale object detection, segmentation, and captioning dataset containing over 330,000 images across 80 object categories."),
        ("What is knowledge distillation?", "Knowledge distillation is a compression technique where a compact student model is trained to reproduce the output probability distribution of a large teacher model."),
        ("What is a monotonic clock?", "A monotonic clock is a time source guaranteed never to step backwards, making it ideal for measuring elapsed duration independently of wall-clock time changes."),
        ("What is an activation function in neural networks?", "An activation function introduces non-linear properties to a neural network, enabling it to learn complex functional mappings between inputs and outputs."),
        ("What is memory bandwidth?", "Memory bandwidth is the rate at which data can be read from or stored into system memory by a processor or accelerator."),
        ("What is the NHWC tensor layout?", "NHWC represents tensor dimensions arranged as batch size, image height, image width, and number of channels, common in mobile inference engines."),
        ("What is a bounding box?", "A bounding box is a rectangular border that encloses a detected object of interest within an image, defined by its spatial coordinates."),
        ("What is JNI in Android?", "The Java Native Interface is a foreign function framework enabling Java and Kotlin code running in the Android Runtime to call native C and C++ libraries."),
        ("What is an attention mechanism?", "An attention mechanism dynamically weights the importance of different elements in an input sequence when computing representations for neural networks.")
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (q, c) in enumerate(qa_samples[:n]):
            rec = {
                "id": idx,
                "question": q,
                "context": c
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Generated {n} text QA samples in {output_path}")


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[2]
    generate_vision_inputs(base / "assets" / "inputs" / "vision", 50)
    generate_text_inputs(base / "assets" / "inputs" / "text.jsonl", 50)

