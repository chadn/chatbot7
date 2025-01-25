import sys

print(sys.path)
#sys.path.append(str(pathlib.Path(__file__).parent.parent))
sys.path.append('./src/')
print(sys.path)

"""
Entry point for the Streamlit application.
Simply imports and runs the main app from src.
"""
from src.streamlit_app import main

if __name__ == "__main__":
    main() 