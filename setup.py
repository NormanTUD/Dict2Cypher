import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Optional: read requirements.txt if exists
try:
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

import setuptools

setuptools.setup(
    name="Dict2Cypher",
    version="0.1.0",
    description="Generate Cypher from dicts",
    author="Norman",
    author_email="your_email@example.com",
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
