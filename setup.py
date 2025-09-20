import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Optional: read requirements.txt if exists
try:
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

setuptools.setup(
    name="dict2cypher",
    version="0.1",
    author="Norman Koch",
    author_email="norman.koch@tu-dresden.de",
    description="Convert Python dicts to Neo4j Cypher queries easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NormanTUD/Dict2Cypher",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
