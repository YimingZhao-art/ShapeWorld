#!/usr/bin/env bash
set -euo pipefail

python generate.py -d examples/agreement/relational-spatial_twoshapes -t agreement \
  -n relational -c configs/agreement/relational/spatial_twoshapes.json -s 5 -i 100 -M -H -G \
  --config-values caption_realizer template_english \
  --world-size 100 --captions-per-instance 1 | tee -a results.txt
