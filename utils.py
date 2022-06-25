import os
import shutil
import yaml
import spectro
import pathlib
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import datetime
from rich.console import Console


def _split(filename):

    # https://pypi.org/project/SongNameSplit/

    # split /a/b/c.dat -> /a/b   c.dat
    head, tail = os.path.split(filename)
    artistname = tail.split(" - ")[0]
    # splitext split the file extension
    songname = os.path.splitext("".join(tail.split(" - ")[1:]))[0]

    return artistname, songname


def fillmeta(path):

    path = pathlib.Path(path)
    if path.is_file():
        _filemetadata(path)
        return

    assert path.is_dir()
    for p in path.glob("**/*"):
        if p.suffix in [".mp3", ".wav", ".flac"]:
            _filemetadata(p)


def _filemetadata(filename):

    # https://from-locals.com/python-mutagen-mp3-id3/

    artist, title = _split(filename)

    # Handling tags error https://github.com/quodlibet/mutagen/issues/327
    try:
        tags = EasyID3(filename)
    except ID3NoHeaderError:
        tags = EasyID3()
        tags.save(filename)

    # Write tags
    tags["title"] = title
    tags["artist"] = artist
    tags.save()

    print(tags.pprint())
    print("\n")


def _artist(filename):

    tags = EasyID3(filename)

    return tags["artist"][0]


def _title(filename):

    tags = EasyID3(filename)

    return tags["title"][0]


def _checkfreq(freq):

    if freq >= 17500:
        return "GOOD"

    else:
        return "BAD"


def hqlist(path):

    hqbands = []
    nohqbands = []

    path = pathlib.Path(path)
    if path.is_file():
        freq = spectro._check_file(path)
        result = _checkfreq(freq)
        band = _artist(path)

        if result == "GOOD":
            hqbands.append(band)
        else:
            nohqbands.append(band)

        return hqbands, nohqbands

    assert path.is_dir()
    for p in path.glob("**/*"):
        if p.suffix in [".mp3", ".wav", ".flac"]:
            freq = spectro._check_file(p)
            result = _checkfreq(freq)
            band = _artist(p)
            song = _title(p)
            if result == "GOOD":
                hqbands.append((band, song))
            else:
                nohqbands.append((band, song))

    # https://stackoverflow.com/questions/6522446/list-of-tuples-to-dictionary
    hq = {}
    for i in hqbands:
        hq.setdefault(i[0], []).append(i[1])

    nohq = {}
    for i in nohqbands:
        nohq.setdefault(i[0], []).append(i[1])

    return hq, nohq


def readfile(filename):

    try:
        with open(filename) as fh:
            dictionary_data = yaml.safe_load(fh)

    except FileNotFoundError as ex:
        print("\tException: {}".format(type(ex).__name__))
        print("\tException message: {}".format(ex))
        return

    return dictionary_data


def copy_merge(dir_src, dir_dst, filebands=None, list_bands=None):

    # dir_src = '/Users/gabrielguerra/Documents/dirfrom'
    # dir_dst = '/Users/gabrielguerra/Documents/dirto'   # dir where we would pate new bands

    if filebands and list_bands:
        raise ValueError("Cannot simultaneously set filebands and list_bands")

    if not (filebands or list_bands):
        raise ValueError("SHould set filebands or list_bands")

    if filebands:
        new_bands = readfile(filebands)

    if list_bands:
        new_bands = list_bands

    disk_bands = []
    for dirnames in next(os.walk(dir_dst))[1]:
        disk_bands.append(dirnames)

    missing_bands = []
    merge_bands = []
    for band in new_bands:
        if band not in disk_bands:
            missing_bands.append(band)
        else:
            merge_bands.append(band)

    console = Console()

    # indication of bands
    print("\nBANDS TO BE ADDED")
    for band in missing_bands:
        console.print(f"[green]+ {band}")

    print("\nBANDS TO BE MERGED")
    for band in merge_bands:
        console.print(f"[yellow]+ {band}")

    for band in missing_bands:
        src = dir_src + "/" + band
        dst = dir_dst + "/" + band
        shutil.copytree(src, dst, dirs_exist_ok=True)

    if merge_bands == []:
        console.print(f"[green]!No bands")
        return

    proceed = input("\nAre you sure you want to merge these bands? (y/n): ")

    if proceed == "y":

        for band in merge_bands:
            src = dir_src + "/" + band
            dst = dir_dst + "/" + band
            shutil.copytree(src, dst, dirs_exist_ok=True)


def print_modified(dir):

    # https://note.nkmk.me/en/python-os-stat-file-timestamp/
    # os.path.getctime('/Users/gabrielguerra/Documents/dirto/Abwarts')

    print(f"\nBANDS ADDED/MERGED in {dir}")

    bands_changed = []
    console = Console()
    path = pathlib.Path(dir)

    now = datetime.datetime.now().timestamp()  # now in float

    assert path.is_dir()
    bands = os.listdir(
        dir
    )  #  https://stackoverflow.com/questions/7099290/how-to-ignore-hidden-files-using-os-listdir
    for band in bands:

        if not band.startswith("."):  # discards hidden directories

            # Wierd error of missing directories in external disk
            try:
                last_modified = os.path.getctime(dir + "/" + band)
            except FileNotFoundError as ex:
                console.print(f"\t[orange]Exception: {type(ex).__name__}")
                console.print(f"\t[orange]Exception message: {ex}")
                continue

            if (now - last_modified) > 0 and (
                now - last_modified
            ) < 180:  # changes in last 3 minutes
                console.print(f"[cyan]{band}")
                bands_changed.append(band)

    # File with added/merged bands

    timemark = datetime.datetime.now().strftime("%d-%m-%-y_%H:%M")
    with open(f"bands_added_{timemark}.yaml", "w") as file:
        yaml.dump(sorted(bands_changed), file, allow_unicode=True)


def timestamps():

    # Path to the file
    path = "/Users/gabrielguerra/Documents/dirto/Grauzone"

    # file modification timestamp of a file
    m_time = os.path.getmtime(path)
    # convert timestamp into DateTime object
    dt_m = datetime.datetime.fromtimestamp(m_time)
    print("Modified on:", dt_m)

    # file creation timestamp in float
    c_time = os.path.getctime(path)
    # convert creation timestamp into DateTime object
    dt_c = datetime.datetime.fromtimestamp(c_time)
    print("Created on:", dt_c)
