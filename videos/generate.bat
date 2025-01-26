@echo off
set PATH=%PATH%;C:\Program Files\MKVToolNix


:: Game of life video
set FILTER=
set FILTER=%FILTER%ratio=0.7:
set FILTER=%FILTER%s=320x240:
set FILTER=%FILTER%rate=24,
set FILTER=%FILTER%edgedetect
::set FILTER=%FILTER%,negate
::set FILTER=%FILTER%,fade=in:0:100
ffmpeg -y -f lavfi -i "life=%FILTER%" -t 60 -pix_fmt yuv420p     -c:v libx264 -preset slow -crf 0 life-h264.mp4
ffmpeg -y -f lavfi -i "life=%FILTER%" -t 60 -pix_fmt yuv420p10le -c:v libx265 -x265-params "aq-mode=0:repeat-headers=0:strong-intra-smoothing=1:bframes=4:b-adapt=2:frame-threads=0:hdr10_opt=0:hdr10=0:chromaloc=0" -preset slow -crf 0 life-h265.mp4
echo done
echo.
echo.



:: Colors animations with timestamp video
set FILTER=
set FILTER=%FILTER%testsrc2=s=1280x720:rate=24:d=60
set FILTER=%FILTER%,scale='-1:min(ih,1080)'
set FILTER=%FILTER%,pad=1920:1080:(ow-iw)/2:(oh-ih)/2
set FILTER=%FILTER%,setsar=1
set FILTER=%FILTER%,format=yuv420p
set FILTER=%FILTER%[v]
::ffmpeg -y -filter_complex "%FILTER%" -map "[v]" -an -c:v libx264 -preset slow -crf 30 testsrc2.mp4
echo done
echo.
echo.


:: Audio tracks (silence)
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000 -vn -c:a mp3 -b:a 128k audio_2ch_128kbps.mp3
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000 -vn -c:a ac3 -b:a 192k audio_2ch_192kbps.ac3
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000 -vn -c:a aac -b:a 192k audio_2ch_192kbps.aac
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=44100 -vn -c:a pcm_s16le audio_silence_44khz.wav
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1(side):sample_rate=44100 -vn -strict -2 -c:a dca -b:a 1510k audio_6ch_1510kbps.dts
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000 -vn -c:a ac3 -b:a 640k audio_6ch_640kbps.ac3
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000 -vn -c:a eac3 -b:a 1152k audio_6ch_1152kbps.eac3
ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=7.1:sample_rate=48000 -vn -c:a eac3 -b:a 1152k audio_8ch_1152kbps.eac3


pause
