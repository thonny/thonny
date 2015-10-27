import os
import sys
import io
import tarfile
import urllib.request


ARCHIVE_URL = 'http://d.pr/f/YqS5+'


def main():
    print('Downloading ensurepip module archive...')
    response = urllib.request.urlopen(ARCHIVE_URL)
    data = response.read()
    tar_f = tarfile.open(fileobj=io.BytesIO(data))

    package_root = sys.path[1]

    print('Extracting files to', package_root)
    os.chdir(package_root)

    try:
        tar_f.extractall()
    except:
        print('Extraction failed! Please ensure you have appropriate '
              'permissions and try again. May you should use "sudo"?')
    else:
        print('All done!\n')


if __name__ == '__main__':
    main()
