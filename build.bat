call .venv/Scripts/activate.bat
pyinstaller --clean specfiles/mvm.spec
pyinstaller --clean specfiles/mvn.spec
docker run --rm -v "%cd%":/src -w /src python:3 /bin/bash -c "pip install -r requirements.txt; pyinstaller specfiles/mvm.spec; pyinstaller specfiles/mvn.spec"