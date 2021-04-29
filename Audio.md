# Audio Notes

## youtube-dl

~~~
python3 -m pip install --user youtube-dl # Install name uses -, runtime name uses _
python3 -m youtube_dl --list-formats URL
python3 -m youtube_dl --format 251 --write-thumbnail URL # Format 251 is audio only Opus @ 122k
~~~

## ffmpeg

~~~
# Find codecs used
ffprobe -hide_banner FILE

# To 'diff' two audio or video files (which may be identical except for metadata), check their hashes
# -map 0 is needed to tell ffmpeg to use all streams available, not just select a default stream
ffmpeg -hide_banner -i FILE -map 0 -f hash -

# Copy audio stream out of file without re-encoding
# -vn causes ffmpeg to skip video streams
# -codec:a copy selects the 'copy' not-a-codec for the audio stream
ffmpeg -hide_banner -i FILE -vn -codec:a copy FILE

# Copy audio streams out of all .webm files in folder to .ogg files
for FILE in *.webm; do ffmpeg -hide_banner -i "$FILE" -vn -codec:a copy "../nightcore/${FILE/.webm/.ogg}"; done

# Get summary of volumes for an audio file
ffmpeg -hide_banner -i FILE -filter:a volumedetect -f null /dev/null

# Get mean volumes for all .ogg files in folder
for file in *.ogg; do echo -n "$file: "; ffmpeg -hide_banner -i "$file" -filter:a volumedetect -f null /dev/null 2>&1 | grep mean_volume; done

# Lower volume of audio file by 10 dB
ffmpeg -hide_banner -i FILE -filter:a "volume=-10.0dB" FILE

# Normalize volume of all .ogg files in folder to -20 dB
for FILE in *.ogg; do
  DELTA=$(ffmpeg -hide_banner -i "$FILE" -filter:a volumedetect -f null /dev/null 2>&1 | grep mean_volume | awk '{print (-20 - $(NF - 1))}')
  ffmpeg -hide_banner -i "$FILE" -filter:a "volume=${DELTA}dB" -v error "${FILE/.ogg/-normalized.ogg}"
done
~~~
