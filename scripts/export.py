#!/usr/bin/env python3

from pathlib import Path
import subprocess
import time
import sys
import os
import logging
import shutil

def usage():
    print("{} output_dir".format(__file__))
    exit()

def get_imagemagick() -> str:
    if sys.platform == "win32":
        return "magick.exe"
    return "convert"

def has_image_magick():
    return subprocess.run("{} --version".format(get_imagemagick()), stdout=subprocess.DEVNULL, shell=True).returncode == 0

if len(sys.argv) != 2:
    usage()

if not has_image_magick():
    print("imagemagick must be installed before using this script")
    exit()

# Logger setup
logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# paths setup
dst = Path(sys.argv[1])
src = Path(os.path.dirname(os.path.realpath(__file__))).parent

res = Path("res")
icon = Path("icon")

counter = 0
total_items = 0

def bench(label, f):
    global counter
    global total_items

    total_items += counter
    counter = 0
    before = time.time()
    f()
    after = time.time()

    if counter:
        logger.info("{}: ".format(label))
        logger.info("\t{} items".format(counter))
        logger.info("\t{:.2}s".format(after - before))


def main():
    bench("textures", lambda: render_psd(res / Path("textures")))
    bench("icon", lambda: render_thumbnail(icon / Path("icon.psd")))
    bench("fonts", lambda: copy_directory(res / Path("fonts")))
    bench("data", lambda: copy_directory(res / Path("data")))

def render_thumbnail(path):
    global counter

    mkdir(dst / path.parent)
    sizes = [512, 256, 128, 64, 32, 16]

    source_file = (src / path)

    for size in sizes:
        target_file = dst / source_file.relative_to(src).with_name("{}@{}.png".format(path.with_suffix("").name, size))

        if not has_changed(target_file, source_file):
            continue

        logger.debug("{} at {size}x{size}:\n\tfrom: {}\n\tto: {}\n".format(source_file.name, source_file, target_file, size=size))
        counter += 1

        subprocess.run("{} \"{}[0]\" -resize {size}x{size} -density 300 -quality 100 \"{}\"".format(get_imagemagick(), source_file, target_file, size=size), shell=True)

def copy_directory(path):
    global counter

    mkdir(dst / path)
    files, directories = [], []

    for x in (src / path).iterdir():
        if x.is_dir():
            directories.append(x)
        else:
            target_file = dst / x.relative_to(src)

            if has_changed(target_file, x):
                files.append(x)

    for directory in directories:
        copy_directory(directory.relative_to(src))

    for f in files:
        source_file = str(f)
        target_file = str(dst / f.relative_to(src))

        logger.debug("{}:\n\tfrom: {}\n\tto: {}\n".format(f.name, source_file, target_file))
        counter += 1

        shutil.copy(source_file, target_file)




def render_psd(path):
    global counter

    mkdir(dst / path)
    files, directories = [], []

    for x in (src / path).iterdir():
        if x.is_dir():
            directories.append(x)
        elif x.suffix == '.psd':
            target_file = dst / x.relative_to(src).with_suffix(".png")

            if has_changed(target_file, x):
                files.append(x)

    for directory in directories:
        render_psd(directory.relative_to(src))

    for f in files:
        source_file = str(f)
        target_file = str(dst / f.relative_to(src).with_suffix('.png'))

        logger.debug("{}:\n\tfrom: {}\n\tto: {}\n".format(f.name, source_file, target_file))
        counter += 1

        subprocess.run("{} \"{}[0]\" {}".format(get_imagemagick(), source_file, target_file), shell=True)
        #psd = PSDImage.open(source_file)
        #psd.composite().save(target_file)

def has_changed(target, source):
    if not target.exists():
        return True

    return target.stat().st_mtime < source.stat().st_mtime

def mkdir(path):
    path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    before = time.time()
    main()
    after = time.time()
    logger.info("processed {} items in {:.2}s\n".format(total_items, after - before))

