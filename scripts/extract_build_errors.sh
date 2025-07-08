#!/bin/bash

INPUT_LOG="dlib_build_full.log"
OUTPUT_LOG="dlib_errors.log"

# Make sure the input log exists
if [ ! -f "$INPUT_LOG" ]; then
    echo "Input log file '$INPUT_LOG' not found."
    exit 1
fi

# Extract likely error lines
grep -iE "error:|fatal error:|CMake Error|Traceback|subprocess.CalledProcessError" "$INPUT_LOG" > "$OUTPUT_LOG"

echo "Extracted likely errors to '$OUTPUT_LOG'"
