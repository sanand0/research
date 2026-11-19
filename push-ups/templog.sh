#!/usr/bin/env bash
# Log CPU/GPU temperature + power every 5 s, fsync'd, so a hard crash still leaves evidence. Usage: ./templog.sh logs/temps.csv &
out=${1:-logs/temps.csv}
cpu=$(grep -l coretemp /sys/class/hwmon/*/name | xargs dirname)/temp1_input
echo "time,cpu_c,gpu_c,gpu_w,gpu_mib,fan_rpm" >> "$out"
while true; do
  g=$(nvidia-smi --query-gpu=temperature.gpu,power.draw,memory.used --format=csv,noheader,nounits | tr -d ' ')
  echo "$(date +%T),$(( $(cat $cpu) / 1000 )),$g,$(sensors 2>/dev/null | awk '/fan1/{print $2; exit}')" >> "$out"
  sync "$out"; sleep 5
done
