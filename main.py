import time
print("Starting main.py")
try:
    print("Importing main from src.main_app...")
    from src.main_app import main
    print("Import successful.")
except Exception as e:
    print("Import failed:", e)
    raise

if __name__ == "__main__":
    main()
