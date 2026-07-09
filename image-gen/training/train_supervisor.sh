#!/bin/bash
# MACAL Empire — Self-healing LoRA training supervisor
#
# WHY THIS EXISTS: a plain `accelerate launch sdxl_train_network.py` run has
# zero memory of its own progress. If it crashes for ANY reason — a Kaggle
# infra SIGKILL, a dead Cloudflare tunnel making Kiro unable to notice, a
# disconnected Kaggle session — all progress is lost and nobody finds out
# until someone manually reconnects and checks. That happened twice in this
# project already (see PROGRESS.md).
#
# WHAT THIS DOES INSTEAD: runs training in a loop, INSIDE Kaggle, independent
# of any tunnel or remote connection. On each crash, it:
#   1. Detects the crash immediately (the `while` loop notices the process exited)
#   2. Finds the latest saved training state (train_config.toml now has
#      save_state = true, which saves optimizer + step count, not just LoRA
#      weights, every 300 steps)
#   3. Automatically relaunches with --resume pointing at that state, so
#      training continues from the last checkpoint instead of step 0
#   4. Logs every attempt with a timestamp to supervisor.log, so reconnecting
#      later immediately shows the FULL crash/recovery history, not just
#      "did it crash" as a mystery to be rediscovered
#   5. Only stops looping once training exits with code 0 (full completion)
#      or after MAX_ATTEMPTS crashes in a row (safety valve against an
#      unrecoverable config error looping forever and burning GPU quota)
#
# Usage (from /kaggle/working/sd-scripts):
#   bash /kaggle/working/eec-telegram-channel/image-gen/training/train_supervisor.sh
#
# Check status any time (even after a fresh tunnel reconnect) with:
#   tail -50 /kaggle/working/supervisor.log
#   cat /kaggle/working/supervisor_status.json

set -u

OUTPUT_DIR="/kaggle/working/macal_empire_lora_output"
LOG_FILE="/kaggle/working/supervisor.log"
STATUS_FILE="/kaggle/working/supervisor_status.json"
TRAIN_CONFIG="/kaggle/working/training_config/train_config.toml"
DATASET_CONFIG="/kaggle/working/training_config/dataset_config.toml"
MAX_ATTEMPTS=8
NUM_PROCESSES="${NUM_PROCESSES:-2}"   # 2 = dual T4, override with NUM_PROCESSES=1 for single-GPU

mkdir -p "$OUTPUT_DIR"
: > "$LOG_FILE"  # fresh log each supervisor run

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

write_status() {
    # attempt, phase, last_step (best-effort grep from training log), timestamp
    local attempt="$1" phase="$2"
    local last_step="unknown"
    if [ -f "$OUTPUT_DIR/attempt_${attempt}.log" ]; then
        # Matches sd-scripts' real tqdm output like "steps:  17%|...| 300/1800"
        # as well as this test's simpler "steps:  300/1800" format.
        last_step=$(grep -oE '[0-9]+/1800' "$OUTPUT_DIR/attempt_${attempt}.log" | tail -1 | cut -d/ -f1)
        [ -z "$last_step" ] && last_step="unknown"
    fi
    python3 -c "
import json
json.dump({
    'attempt': $attempt,
    'phase': '$phase',
    'last_step_seen': '$last_step',
    'timestamp_utc': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
}, open('$STATUS_FILE', 'w'))
"
}

find_latest_state_dir() {
    # sd-scripts saves state dirs named like:
    #   macalempire_style_sdxl-step00000300-state/
    ls -1d "$OUTPUT_DIR"/*-state 2>/dev/null | sort -t- -k2 -V | tail -1
}

cd /kaggle/working/sd-scripts || { log "FATAL: sd-scripts directory not found"; exit 1; }

attempt=0
while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
    attempt=$((attempt + 1))
    resume_dir=$(find_latest_state_dir)

    if [ -n "$resume_dir" ]; then
        log "Attempt $attempt: resuming from state: $resume_dir"
        write_status "$attempt" "resuming"
        RESUME_ARGS="--resume $resume_dir"
    else
        log "Attempt $attempt: starting fresh (no prior state found)"
        write_status "$attempt" "starting"
        RESUME_ARGS=""
    fi

    # NCCL_P2P_DISABLE / NCCL_IB_DISABLE: Kaggle's T4 pairs have no NVLink,
    # and direct peer-to-peer GPU communication under NCCL has been the most
    # likely cause of the unexplained SIGKILL crash seen in this project's
    # first dual-GPU attempt (crashed at step 120 with no CUDA OOM error —
    # consistent with an NCCL/P2P timeout, not a memory problem). Forcing
    # communication through the CPU is slower per-step but far more stable
    # on this specific hardware pairing.
    NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1 \
        accelerate launch --num_cpu_threads_per_process 2 --num_processes "$NUM_PROCESSES" \
        sdxl_train_network.py \
        --config_file "$TRAIN_CONFIG" \
        --dataset_config "$DATASET_CONFIG" \
        --max_data_loader_n_workers 0 \
        $RESUME_ARGS \
        > "$OUTPUT_DIR/attempt_${attempt}.log" 2>&1
    exit_code=$?

    if [ "$exit_code" -eq 0 ]; then
        log "Attempt $attempt: training COMPLETED successfully (exit code 0)."
        write_status "$attempt" "completed"
        exit 0
    fi

    log "Attempt $attempt: training exited with code $exit_code (crash or manual stop)."
    log "  Last 15 log lines from this attempt:"
    tail -15 "$OUTPUT_DIR/attempt_${attempt}.log" | while IFS= read -r line; do log "    $line"; done
    write_status "$attempt" "crashed_exit_${exit_code}"

    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
        log "  Will auto-resume in 15s (attempt $((attempt + 1))/$MAX_ATTEMPTS)..."
        sleep 15
    fi
done

log "FATAL: reached MAX_ATTEMPTS ($MAX_ATTEMPTS) without training completing. Stopping to avoid burning GPU quota on a likely config/dataset error rather than a transient infra crash. Check attempt_*.log files for the real error."
write_status "$attempt" "gave_up_max_attempts"
exit 1
