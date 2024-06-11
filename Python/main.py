import subprocess

def run_main():
    try:
        subprocess.run(["python", "Face_log_in.py"])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_main()