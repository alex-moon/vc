#!/bin/bash

ffmpeg -y -i "steps/%04d.png" \
  -b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2 \
  -filter:v "minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:fps=60'" \
  sofar.mp4

ffmpeg -i sofar.mp4 -i app/assets/watermark.png -filter_complex "overlay=0:0" \
  sofar-watermarked.mp4
