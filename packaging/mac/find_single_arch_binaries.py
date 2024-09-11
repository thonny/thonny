import os
import subprocess


def is_universal_binary_or_non_binary(file_path):
    try:
        # Use the `file` command to get information about the binary
        output = subprocess.check_output(['file', file_path], text=True)

        # Check if the binary is a fat binary (universal binary)
        if 'fat binary' in output:
            return True

        if "Mach-O universal binary with 2 architectures" in output:
            return True

        if "Mach-O" not in output:
            return True

        # Check if the binary contains multiple architectures
        elif 'Mach-O' in output and 'x86_64' in output and 'arm64' in output:
            return True
        return False
    except Exception as e:
        print(f"Error checking file {file_path}: {e}")
        return False


def find_non_universal_binaries(root_dir):
    non_universal_binaries = []

    # Walk through the directory recursively
    for root, dirs, files in os.walk(root_dir):
        file:str
        for file in files:
            if file.endswith(".py") or file[:-1].endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            if not is_universal_binary_or_non_binary(file_path):
                non_universal_binaries.append(file_path)

    return non_universal_binaries


def main():
    directory_to_search = 'build'  # Replace with your directory path
    non_universal_binaries = find_non_universal_binaries(directory_to_search)

    print(f"Non-universal binaries found in {directory_to_search}:")
    for binary in non_universal_binaries:
        print(binary)


if __name__ == "__main__":
    main()
