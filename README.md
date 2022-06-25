# Automation of workflow for analysis and organization of music

This is a script for automation of some tasks that music enthusiasts music may be facing when they organize their music. Ussually, anyone who wants to have his music classified makes the following steps:

1) User collects some songs into a folder.
2) He analyses the quality of each one.
3) The high quality songs are saved in a music library (for example ITunes directory).
4) He edits the tags of the songs using a music player (ITunes)
5) He makes a backup of the new added files on this library into a external device.

With the scripts of this repo, steps 2, 4, and 5 of this workflow have been automated.

# How it works

Before running the script, it is necessary to locate all files into one directory. In addition, all the files need to be named with the format: Artist - Song.

The script will ask for three arguments:

```Python
def  main(songs, src, dst): 
```

- songs: directory where audio files are located,
- src: directory of the music library where the new audio files will be located,
- dst: directory  where the new audio files will saved as backup,

## Filling tags on the audio file

The script will read the ID3 tags artist and title of the audio file and will fill it

## Analyzing the quality of the audio file

This is done using the dependecy  a fork of the **spectro** repo to get the highest frequency in the song. By default, the script catalog high quality only frequencies above 17500 Hz (~320Kbps). Also, the script generate two YAML files, one with the songs with good HQ and the other with the songs with poor HQ.

## Adding audio files to the Music library

During the script execution, the script will ask for confirmation about the addition of the songs into the music library. In the case of using ITunes, every time you play a song , the player will add the fle into its music library if it did not exist.

```Python
listened = False
while  listened == False:
	answer = input("\nDid you listened with Apple Music? (y/n): ")
	listened = False  if  answer == "n"  else  True
```

## Copy of audio files from Music library to other directory

The script will classify the HQ bands into missing and merge according to what it finds in the destination directory. The first ones are copied inmediatley. In the case of bands which already exist in the destination directory, the script will ask for confirmation. The operation will merge the files.

```Python
proceed = input("\nAre you sure you want to merge these bands? (y/n): ")
if  proceed == "y":
for  band  in  merge_bands:
src = dir_src + "/" + band
dst = dir_dst + "/" + band
shutil.copytree(src, dst, dirs_exist_ok=True)
```

## Print out the results

The script prints the bands that were added or merged into the console. Also, it generates a YAML file listing them
