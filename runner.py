import os
import re
import subprocess
import tempfile

JAVA_IMAGES = {
    "8": "eclipse-temurin:8-jdk",
    "11": "eclipse-temurin:11-jdk", 
    "17": "eclipse-temurin:17-jdk",
    "21": "eclipse-temurin:21-jdk",
}

def extract_class_name(java_code: str) -> str:
    match = re.search(r'public\s+class\s+(\w+)', java_code)
    return match.group(1) if match else "Main"

def run_java(java_version: str, java_code: str) -> dict[str, bool | int | str]:
    print("Inside run java method!!")
    if java_version not in JAVA_IMAGES:
        raise ValueError("Unsupported Java version")
    print("Selected Java version:", java_version)
    class_name = extract_class_name(java_code)
    print("Class name:", class_name)
    with tempfile.TemporaryDirectory() as tmp:
        java_file = os.path.join(tmp, f"{class_name}.java")
        with open(java_file, "w") as f:
            f.write(java_code)

        image = JAVA_IMAGES[java_version]
        print("Image name:", image)
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{tmp}:/app",
            "-w", "/app",
            image,
            "sh", "-c", f"javac {class_name}.java && java {class_name}"
        ]
        print("Command value:", cmd)
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("Result :", result)

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
