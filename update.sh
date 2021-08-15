ffmpeg -y -i input/input-%04d.png -b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2 -filter:v minterpolate=mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60 results/video-sixth-attempt.mp4
