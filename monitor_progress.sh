#!/bin/bash
# Monitor data generation progress

while true; do
    if [ -f teacher_data_test.jsonl ]; then
        count=$(wc -l < teacher_data_test.jsonl)
        pct=$(echo "scale=1; ($count/5000)*100" | bc)
        echo "[$(date +%H:%M:%S)] Progress: $count/5000 ($pct%)"
    else
        echo "[$(date +%H:%M:%S)] Waiting for generation to start..."
    fi
    sleep 60
done
