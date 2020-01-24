from zipfile import ZipFile
import os, sys
import shutil

# recursively merge two folders including subfolders
# from https://lukelogbook.tech/2018/01/25/merging-two-folders-in-python/
def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, _, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)


os.mkdir("lib")
with ZipFile("PyGTK2.24.0-legacy.zip") as libfile:
    libfile.extractall("lib")

if os.path.isdir("C:\\Python27"):
    mergefolders("lib", "C:\\Python27\\Lib")

