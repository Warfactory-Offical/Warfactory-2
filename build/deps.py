import sys
import subprocess
import tempfile
import shutil
import atexit
import os


def ensure_dependencies(packages):
    """
    Checks for packages and installs them into a temporary directory if missing.
    Adds the temporary directory to sys.path.
    """

    try:
        temp_dir = tempfile.mkdtemp()
        print(f"Created temporary directory for dependencies: {temp_dir}")
        sys.path.insert(0, temp_dir)
    except OSError as e:
        print(f"Failed to create temporary directory for dependencies: {e}")
        exit("Could not create temporary directory for dependencies.")

    def _cleanup():
        """Removes the temporary directory used for dependencies."""
        if temp_dir and os.path.exists(temp_dir):
            print(f"Cleaning up temporary dependencies directory: {temp_dir}")
            try:
                shutil.rmtree(temp_dir)
                _temp_dir = None
            except OSError as e:
                print(f"Warning: Could not remove temp directory {temp_dir}: {e}")
        else:
            print("No temporary directory to clean up or already cleaned.")
    atexit.register(_cleanup)


    try:
        print(f"Installing dependencies to {temp_dir}...")
        cmd = [
                  sys.executable,
                  "-m",
                  "pip",
                  "install",
                  "--target",
                  temp_dir,
              ] + packages

        subprocess.run(
            cmd,
            check=True, # Raise CalledProcessError on failure
            capture_output=True,
            text=True,
        )
        print("Dependencies installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies using pip.")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        print(f"Stderr:\n{e.stderr}")
        print(f"Stdout:\n{e.stdout}")
    except FileNotFoundError:
        # This might happen if '{your_python_executable} -m pip' cannot be run
        print(f"Error: '{sys.executable} -m pip' command not found.")
        print("Please ensure pip is installed and accessible for this Python.")
    except Exception as e:
        print(f"An unexpected error occurred during dependency setup: {e}")



