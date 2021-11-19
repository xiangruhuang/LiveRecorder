
import moviepy.editor as me
import sys

filename = sys.argv[1]
clip = me.VideoFileClip(filename)
clip.audio.write_audiofile(filename.replace('.flv', '.mp3'))

