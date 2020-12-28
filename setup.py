import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dataStore", # Replace with your own username
    version="0.0.1",
    author="Pavan K",
    author_email="pavankasina29@gmail.com",
    description="Freshworks – Backend Assignment : To build a file-based key-value data store that supports the basic CRD (create, read, and delete) operations.",
    long_description = open("README.txt").read() + '\n\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type = "text/markdown",
    url="https://github.com/PavanCyborg/Freshworks-Assignment.git",
    packages = setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows :: Windows10",
    ],
    python_requires='>=3.7',
)
