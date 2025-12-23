#!/bin/bash
# -----------------------------------------------------------------------------
# Script Name: run.sh
# Description: Evaluates the INF-X-Retriever model on various tasks.
# Usage: ./run.sh
# -----------------------------------------------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

# --- Configuration Variables ---
# Set default values if not provided in the environment

# Model name or path
MODEL_NAME="${MODEL_NAME:-inf}"

# Directory for output results
OUTPUT_DIR="${OUTPUT_DIR:-./output/INF-X-Retriever}"
# OUTPUT_DIR="${OUTPUT_DIR:-./output/inf-retriever-v1-pro}"

# Whether to run rewrite evaluation (true/false)
REWRITE_EVAL="${REWRITE_EVAL:-true}"

# Folder containing rewrite data
REWRITE_FOLDER="${REWRITE_FOLDER:-./rewrite_data}"

# Long context test (true/false)
LONG_CONTEXT="${LONG_CONTEXT:-false}"

# Debug mode (true/false)
DEBUG="${DEBUG:-false}"

# Batch size for encoding
ENCODE_BATCH_SIZE="${ENCODE_BATCH_SIZE:-16}"

# List of tasks to evaluate
TASKS=(
    "biology"
    "earth_science"
    "economics"
    "pony"
    "psychology"
    "robotics"
    "stackoverflow"
    "sustainable_living"
    "aops"
    "leetcode"
    "theoremqa_theorems"
    "theoremqa_questions"
)

# --- Main Execution ---

echo "=========================================="
echo "Starting Evaluation Script"
echo "Model: ${MODEL_NAME}"
echo "Output Directory: ${OUTPUT_DIR}"
echo "Debug Mode: ${DEBUG}"
echo "=========================================="

for TASK_NAME in "${TASKS[@]}"; do
    echo "Processing task: ${TASK_NAME}"

    # Construct the command using an array to handle arguments safely
    CMD=(
        python run.py
        --task "${TASK_NAME}"
        --output_dir "${OUTPUT_DIR}"
        --model "${MODEL_NAME}"
        --encode_batch_size "${ENCODE_BATCH_SIZE}"
    )

    # Conditionally add arguments
    if [ "${REWRITE_EVAL}" = "true" ]; then
        CMD+=(--input_file "${REWRITE_FOLDER}/${TASK_NAME}_queries.json")
    fi

    if [ "${LONG_CONTEXT}" = "true" ]; then
        CMD+=(--doc_max_length "40960")
        CMD+=(--long_context)
    fi

    if [ "${DEBUG}" = "true" ]; then
        CMD+=(--debug)
    fi

    # Print the command being executed for transparency
    echo "Running command: ${CMD[*]}"

    # Execute the command
    "${CMD[@]}"

    echo "Task '${TASK_NAME}' completed."
    echo "------------------------------------------"
done

echo "All tasks completed successfully."
