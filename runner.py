import os
import re
import subprocess
import tempfile
import uuid
import shutil
import sys

JAVA_HOMES = {
    "8": "/usr/lib/jvm/java-8-openjdk-amd64",
    "11": "/usr/lib/jvm/java-11-openjdk-amd64", 
    "17": "/usr/lib/jvm/java-17-openjdk-amd64",
    "21": "/usr/lib/jvm/java-21-openjdk-amd64",
}

def extract_class_name(java_code: str) -> str:
    match = re.search(r'public\s+class\s+(\w+)', java_code)
    return match.group(1) if match else "Main"

def run_java(java_version: str, java_code: str) -> dict[str, bool | int | str]:
    if java_version not in JAVA_HOMES:
        raise ValueError("Unsupported Java version")

    class_name = extract_class_name(java_code)
    
    # Use unique temp directory
    unique_id = str(uuid.uuid4())[:8]
    tmp_dir = f"/tmp/java-runner-{unique_id}"
    os.makedirs(tmp_dir, exist_ok=True)
    
    java_file = os.path.join(tmp_dir, f"{class_name}.java")
    with open(java_file, "w") as f:
        f.write(java_code)

    java_home = JAVA_HOMES[java_version]
    javac_path = os.path.join(java_home, "bin", "javac")
    java_path = os.path.join(java_home, "bin", "java")
    
    # Compile Java code
    compile_cmd = [javac_path, java_file]
    compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=tmp_dir)
    
    if compile_result.returncode != 0:
        # Clean up and return compilation error
        try:
            shutil.rmtree(tmp_dir)
        except:
            pass
        return {
            "success": False,
            "exit_code": compile_result.returncode,
            "stdout": "",
            "stderr": compile_result.stderr.strip(),
        }
    
    # Run Java code
    run_cmd = [java_path, "-cp", tmp_dir, class_name]
    run_result = subprocess.run(run_cmd, capture_output=True, text=True)
    
    # Clean up the directory
    try:
        shutil.rmtree(tmp_dir)
    except:
        pass

    return {
        "success": run_result.returncode == 0,
        "exit_code": run_result.returncode,
        "stdout": run_result.stdout.strip(),
        "stderr": run_result.stderr.strip(),
    }

def main(java_version: str, java_file_path: str):
    java_code = open(java_file_path).read()
    result = run_java(java_version, java_code)
    execution_succeeded = result["success"]
    if execution_succeeded:
        print("✅ Java executed successfully")
        print(result["stdout"])
    else:
        print("❌ Java execution failed")
        print("Exit code:", result["exit_code"])
        print("Error:")
        print(result["stderr"])

# Run with command 'python runner.py 11 java_templates/Main8.java'
if __name__ == "__main__":
    # Check the number of arguments (script name + 2 inputs)
    if len(sys.argv) != 3:
        print("Usage: python runner.py <java_version> <java_file_path>" )
        sys.exit(1)  # Exit if the number of arguments is incorrect

    java_version = sys.argv[1]
    java_file_path = sys.argv[2]
    main(java_version, java_file_path)
