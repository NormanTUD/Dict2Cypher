import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Optional: read requirements.txt if exists
try:
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

# Prüfen, dass dict2cypher.py existiert
module_file = "dict2cypher.py"
if not os.path.exists(module_file):
    raise FileNotFoundError(f"{module_file} not found in repo root!")

setuptools.setup(
    name="Dict2Cypher",
    version="0.1.0",
    description="Generate Cypher from dicts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Norman Koch",
    author_email="norman.koch@tu-dresden.de",
    py_modules=["dict2cypher"],   # <- die magische Zeile: installiert dict2cypher.py
    python_requires=">=3.9",
    install_requires=requirements,  # dynamisch aus requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
