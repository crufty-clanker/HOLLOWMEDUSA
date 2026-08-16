"""Fix NixOS libstdc++.so.6 issue for async SQLAlchemy tests."""
import os
import subprocess
import sys


def fix_libstdc():
    """Find and preload libstdc++.so.6 from Nix store."""
    nix_store = "/nix/store"
    for root, _dirs, files in os.walk(nix_store):
        if "libstdc++.so.6" in files:
            lib_path = os.path.join(root, "libstdc++.so.6")
            os.environ["LD_PRELOAD"] = lib_path
            print(f"Preloaded: {lib_path}")
            return True
    return False


if __name__ == "__main__":
    if fix_libstdc():
        # Re-exec with LD_PRELOAD set
        os.execvp(sys.argv[1], sys.argv[1:])
    else:
        print("Warning: libstdc++.so.6 not found, tests may fail")
        # Run the command anyway
        subprocess.run(sys.argv[1:])
