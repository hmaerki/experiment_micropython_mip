"""
https://github.com/micropython/micropython-lib/blob/master/tools/build.py
"""
import json
import os
import shutil
import sys
import hashlib
import pathlib
import subprocess
import tempfile

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_REPO = DIRECTORY_OF_THIS_FILE.parent

DIRECTORY_SRC = DIRECTORY_REPO / "src"
assert DIRECTORY_SRC.is_dir()

DIRECTORY_PACKAGES = DIRECTORY_REPO / "docs" / "package"

MYPY_VERSION = 6
PACKAGE_NAME = "dryer2023"

DIRECTORY_PACKAGE = DIRECTORY_PACKAGES / PACKAGE_NAME / str(MYPY_VERSION)
DIRECTORY_PACKAGE.mkdir(parents=True, exist_ok=True)

BRANCH = "main"
HASH_PREFIX_LEN = 12


# Returns the sha256 of the specified file object.
def _get_file_hash(mpy_code: bytes):
    hs256 = hashlib.sha256()
    hs256.update(mpy_code)
    return hs256.hexdigest()


# Copy src to "file"/{short_hash[0:2]}/{short_hash}.
def _write_hashed_file(
    package_name: str,
    mpy_code: bytes,
    py_code: str,
    target_path: str,
    out_file_dir: pathlib.Path,
    hash_prefix_len: int,
):
    # Generate the full sha256 and the hash prefix to use as the output path.
    file_hash = _get_file_hash(mpy_code)
    short_file_hash = file_hash[:hash_prefix_len]
    # Group files into subdirectories using the first two bytes of the hash prefix.
    output_file = os.path.join(short_file_hash[:2], short_file_hash)
    output_file_path = out_file_dir / output_file

    # Hack: Just ignore hash conflicts
    output_file_path.unlink(missing_ok=True)

    if output_file_path.is_file():
        # If the file exists (e.g. from a previous run of this script), then ensure
        # that it's actually the same file.
        if not _identical_files(mpy_code.name, output_file_path):
            print(
                error_color("Hash collision processing:"),
                package_name,
                file=sys.stderr,
            )
            print("  File:        ", target_path, file=sys.stderr)
            print("  Short hash:  ", short_file_hash, file=sys.stderr)
            print("  Full hash:   ", file_hash, file=sys.stderr)
            with open(output_file_path, "rb") as f:
                print("  Target hash: ", _get_file_hash(f), file=sys.stderr)
            print("Try increasing --hash-prefix (currently {})".format(hash_prefix_len))
            sys.exit(1)
    else:
        # Create new file.
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_bytes(mpy_code)
        output_file_path.with_suffix(".py").write_text(py_code)

    return short_file_hash


def main():
    package_json = {
        "hashes": [],
        "deps": [
            [
                "umqtt.simple",
                "latest",
            ]
        ],
        "version": "0.1",
    }

    for filename_py in (DIRECTORY_SRC / PACKAGE_NAME).glob("*.py"):
        with tempfile.NamedTemporaryFile(
            mode="rb", suffix=".mpy", delete=True
        ) as mpy_tempfile:
            proc = subprocess.run(
                [
                    "python", "-m",
                    "mpy-cross",
                    "-o",
                    mpy_tempfile.name,
                    str(filename_py),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                raise Exception(
                    f"{proc.args}: returned {proc.returncode}:\n {proc.stdout} \n---\n {proc.stderr}"
                )

            target_path = f"{filename_py.stem}.mpy"
            short_mpy_hash = _write_hashed_file(
                PACKAGE_NAME,
                mpy_tempfile.read(),
                filename_py.read_text(),
                target_path=target_path,
                out_file_dir=DIRECTORY_PACKAGE,
                hash_prefix_len=HASH_PREFIX_LEN,
            )

            # Add the file to the package json.
            target_path_mpy = target_path[:-2] + "mpy"
            package_json["hashes"].append((target_path_mpy, short_mpy_hash))

        with (DIRECTORY_PACKAGE / "latest.json").open("w") as f:
            json.dump(package_json, f ,indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
