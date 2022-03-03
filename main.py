import io
import os
import os.path
import subprocess
import sys
import threading
import concurrent.futures

OUTPUT_DIR = "out/"
WORKING_DIR = "work/"
BUILDTOOLS = os.path.abspath("BuildTools.jar")

external_flags = {
    "--disable-java-check",
    "--generate-source",
    "--generate-docs",
}


class Printer(io.TextIOWrapper):
    def __init__(self):
        super().__init__(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        self.lock = threading.Lock()

    def write(self, __s: str) -> int:
        print("aaa")
        with self.lock:
            self.print("INFO", __s, delimiter="")
            return len(__s)

    def writelines(self, __lines) -> None:
        with self.lock:
            for line in __lines:
                self.write(line)

    def print(self, level, text, version="general", delimiter="\n"):
        with self.lock:
            print("[%s/%s/%s] %s" % (level, version, threading.current_thread().name, text), end=delimiter)

    def info(self, text, version="general"):
        self.print("INFO", text, version)

    def error(self, text):
        self.print("ERROR", text)


printer = Printer()
printf = printer.info


def checkEnv():
    if not os.path.isfile(BUILDTOOLS):
        print("BuildTools.jar not found")
        exit(1)

    if os.name == "nt":
        java_version = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        java_version = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if java_version.returncode != 0:
        print(java_version.stderr.decode("utf-8"))
        print("Java not found: Process returned with code %d" % java_version.returncode)
        exit(1)


def setupBuild(version, output_dir, working_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(working_dir, exist_ok=True)


def runBuildTools(version, working_dir, output_dir):
    printf("Running BuildTools...", version)
    arguments = ["java", "-jar", BUILDTOOLS, "--rev", version]
    arguments.extend(external_flags)
    arguments.append("--output")
    arguments.append(output_dir)

    if os.name == "nt":
        process = subprocess.Popen(arguments, cwd=working_dir,
                                   stdout=subprocess.PIPE, stderr=sys.stderr, shell=True)
    else:
        process = subprocess.Popen(arguments, cwd=working_dir,
                                   stdout=subprocess.PIPE, stderr=sys.stderr)

    while process.poll() is None:
        line = process.stdout.readline()
        printf(line.decode("utf-8").strip(), version)

    exit_code = process.wait()

    if exit_code != 0:
        printf("BuildTools failed with exit code %d" % exit_code, version)
        os.rmdir(output_dir)
    else:
        printf(version + " was built successfully.", version)


def build(version):
    output_dir = OUTPUT_DIR + version + "/"
    working_dir = WORKING_DIR + version + "/"
    printf("Build phase started.", version)
    printf("Setting up the build session.", version)
    setupBuild(output_dir, working_dir, output_dir)
    printf("Building...", version)
    runBuildTools(version, working_dir, output_dir)
    printf("Cleaning...", version)
    os.rmdir(working_dir)


def main():
    checkEnv()

    with open("versions.txt", "r") as f:
        versions = f.read().splitlines()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(build, versions)

    printf("All versions were built successfully.")


if __name__ == "__main__":
    main()
