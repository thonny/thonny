#!/usr/bin/env bash

export TARGET_DIR=thonny/plugins/circuitpython/typeshed/stdlib

rm -rf $TARGET_DIR
pip3 install --upgrade --target $TARGET_DIR circuitpython-stubs

echo "RENAMING DIRS"
for item in ${TARGET_DIR}/*-stubs; do
  mv "$item" "${item/-stubs/}"
done

echo "COMPILING BOARDS"
python3 <<EOF
import os.path
pin_names = set()
board_defs_dir = os.path.join(os.environ["TARGET_DIR"], "board_definitions")
for name in os.listdir(board_defs_dir):
    def_path = os.path.join(board_defs_dir, name, "__init__.pyi")
    if os.path.isfile(def_path):
        with open(def_path, encoding="utf-8") as fp:
            for line in fp:
                if ": microcontroller.Pin" in line:
                      name, _ = line.split(":", maxsplit=1)
                      pin_names.add(name)

board_pyi = os.path.join(os.environ["TARGET_DIR"], "board", "__init__.pyi")
with open(board_pyi, "a", encoding = "utf-8") as fp:
    fp.write("\n\nfrom microcontroller import Pin\n\n")
    for name in sorted(pin_names):
        if not name[0].isnumeric():
            fp.write(f"{name}: Pin\n")

EOF

echo "COPYING STDLIB FROM MP"
MP_SOURCE=thonny/plugins/micropython/typeshed/stdlib

cp -r ${MP_SOURCE}/_typeshed $TARGET_DIR
cp -r ${MP_SOURCE}/asyncio $TARGET_DIR
cp -r ${MP_SOURCE}/collections $TARGET_DIR
cp ${MP_SOURCE}/ucollections.pyi $TARGET_DIR/collections/__init__.pyi
cp ${MP_SOURCE}/_collections_abc.pyi $TARGET_DIR

cp ${MP_SOURCE}/_asyncio.pyi $TARGET_DIR

cp ${MP_SOURCE}/builtins.pyi $TARGET_DIR
cp ${MP_SOURCE}/gc.pyi $TARGET_DIR
cp ${MP_SOURCE}/math.pyi $TARGET_DIR
cp ${MP_SOURCE}/micropython.pyi $TARGET_DIR

cp ${MP_SOURCE}/uarray.pyi $TARGET_DIR/array.pyi
cp ${MP_SOURCE}/ubinascii.pyi $TARGET_DIR/binascii.pyi
cp ${MP_SOURCE}/uerrno.pyi $TARGET_DIR/errno.pyi
cp ${MP_SOURCE}/uhashlib.pyi $TARGET_DIR/hashlib.pyi
cp ${MP_SOURCE}/uio.pyi $TARGET_DIR/io.pyi
cp ${MP_SOURCE}/ujson.pyi $TARGET_DIR/json.pyi
cp ${MP_SOURCE}/uos.pyi $TARGET_DIR/os.pyi
cp ${MP_SOURCE}/uplatform.pyi $TARGET_DIR/platform.pyi
cp ${MP_SOURCE}/urandom.pyi $TARGET_DIR/random.pyi
cp ${MP_SOURCE}/ure.pyi $TARGET_DIR/re.pyi
cp ${MP_SOURCE}/uselect.pyi $TARGET_DIR/select.pyi
cp ${MP_SOURCE}/ustruct.pyi $TARGET_DIR/struct.pyi
cp ${MP_SOURCE}/usys.pyi $TARGET_DIR/sys.pyi
cp ${MP_SOURCE}/utime.pyi $TARGET_DIR/time.pyi

echo "CLEANING"
rm -r ${TARGET_DIR:?}/bin

echo "CREATING README"
cat <<EOF > readme.txt
Adapted from circuitpython-stubs and Micropython typeshed (thonny/plugins/micropython/typeshed)
EOF
