import os
import shutil
import sqlite3
import argparse


# http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
def copy_file_create_subdirs(src_file, dst_file):
    if not os.path.exists(os.path.dirname(dst_file)):
        try:
            os.makedirs(os.path.dirname(dst_file))

        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # copy2 should keep metadata intact
    shutil.copy2(src_file, dst_file)


def extract_media_from_backup(backup_dir, out_dir):
    conn = sqlite3.connect(os.path.join(backup_dir, 'Manifest.db'))
    
    # simple query to get only media (without thumbnails)
    query = "SELECT * FROM Files WHERE domain = 'CameraRollDomain' AND relativePath LIKE '%Media/DCIM%'"

    for subfile, _, relpath, _, _ in conn.cursor().execute(query):
        # files are stored in subdirectories, that match first 2 characters of their names
        subdir = subfile[:2]

        # abspath will normalize path separators (windows uses reverse slashes, but relpath has forward ones)
        # doing it on src_file is not really necessary, but won't hurt
        src_file = os.path.abspath(os.path.join(backup_dir, subdir, subfile))
        dst_file = os.path.abspath(os.path.join(out_dir, relpath))
        
        try:
            copy_file_create_subdirs(src_file, dst_file)
            print src_file
            print dst_file, '\n'

        except Exception as e:
            print e, '\n'


if __name__ == "__main__":
    desc = "Copies media files (that were stored in 'Media/DCIM/' directory) to a " \
           "specified location, retaining directory structure"

    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('backup_dir', help='Location of backup directory')
    parser.add_argument('out_dir', help='Destination directory, relative to which ' \
                        'files would be copied, according to original directory structure')
    
    args = parser.parse_args()
    extract_media_from_backup(args.backup_dir, args.out_dir)

