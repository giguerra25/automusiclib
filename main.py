#!./.env/bin/python
import utils as CPT
import yaml
import sys
import os


def main(songs, src, dst):

    # https://pyinstaller.org/en/stable/runtime-information.html
    # https://stackoverflow.com/questions/48617861/app-made-using-pyinstaller-closes-straight-away
    cwd = os.getcwd()

    dir_songs = songs
    dir_src = src
    dir_dst = dst

    # Fill tags MP3s

    CPT.fillmeta(dir_songs)

    # Analysis of quality

    hqlist, nohqlist = CPT.hqlist(dir_songs)

    # YAML file
    # https://dpinte.wordpress.com/2008/10/31/pyaml-dump-option/

    with open(cwd + "/" + "bands2add.yaml", "w") as file:
        yaml.dump(hqlist, file, allow_unicode=True)
    with open(cwd + "/" + "bandsNo2add.yaml", "w") as file:
        yaml.dump(nohqlist, file, allow_unicode=True)

    # Time to listen new music
    listened = False
    while listened == False:

        answer = input("\nDid you listened with Apple Music? (y/n): ")
        listened = False if answer == "n" else True

    #  copy and merge bands

    # filebands = cwd + "/" + "bands2add.yaml"
    CPT.copy_merge(dir_src, dir_dst, list_bands=hqlist)

    # Print copied and merged bands with colors

    CPT.print_modified(dir_dst)


if __name__ == "__main__":

    try:
        songs = sys.argv[1]
    except IndexError:

        loop1 = True
        while loop1:
            songs = input(f"Directory with songs: ")
            if songs:
                loop1 = False

    try:
        src = sys.argv[2]
    except IndexError:
        loop2 = True
        src = "/Users/gabrielguerra/Music/iTunes/iTunes Media/Music"
        print(f"Directory iTunes (default) '{src}'.")

        while loop2:
            ans = input(f"Change it? (y/n): ")
            if ans == "y":
                src = input("Directory (from): ")
                loop2 = False
            elif ans == "n":
                loop2 = False

    try:
        dst = sys.argv[3]
    except IndexError:
        loop3 = True
        dst = "/Volumes/GABRIEL/resp laptop vieja/Musica Todo"
        print(f"Directory Hard Disk (default) '{dst}'.")

        while loop3:
            ans = input(f"Change it? (y/n): ")
            if ans == "y":
                dst = input("Directory (to): ")
                loop3 = False
            elif ans == "n":
                loop3 = False

    main(songs, src, dst)
