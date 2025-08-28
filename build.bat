call .venv/Scripts/activate.bat
pyinstaller --clean --onefile mvm.py
pyinstaller --clean --onefile mvn.py