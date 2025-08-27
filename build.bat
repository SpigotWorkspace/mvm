call .venv/Scripts/activate.bat
pyinstaller --clean specfiles/mvm.spec
pyinstaller --clean specfiles/mvn.spec