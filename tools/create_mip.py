import pathlib
import subprocess

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_REPO = DIRECTORY_OF_THIS_FILE.parent

DIRECTORY_SRC = DIRECTORY_REPO / "src"
assert DIRECTORY_SRC.is_dir()

DIRECTORY_PACKAGES = DIRECTORY_REPO / "docs" / "package"

MYPY_VERSION = 6
PACKAGE_NAME = "dryer2023"


def main():
    directory_package = DIRECTORY_PACKAGES / PACKAGE_NAME
    for filename_py in (DIRECTORY_SRC / PACKAGE_NAME).glob("*.py"):
        # filename_mpy = DIRECTORY_PACKAGES / PACKAGE_NAME / (filename_py.stem + ".mpy")
        # print(filename_py, filename_mpy)
        proc = subprocess.run(
            [
                "mpy-cross",
                "-o",
                f"{directory_package/filename_py.stem}.mpy",
                str(filename_py),
            ],
            capture_output=True,
            check=True,
        )
        if proc.returncode != 0:
            raise Exception(f"{proc.args}: returned {proc.returncode}:\n {proc.stdout} \n---\n {proc.stdout}")


if __name__ == "__main__":
    main()
