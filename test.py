import subprocess

result = subprocess.run(["git", "pull"], capture_output=True, text=True)

output = result.stdout
error = result.stderr

print(f"output: {len(output)}, error: {len(error)}")
