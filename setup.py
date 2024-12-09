from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A Package Management Tool For C++ Libraries."

setup(
    name="cpakage",
    version="0.0.1",
    author="Kamran Najafi",
    author_email="",
    description="A package management tool for C++ libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cpakage.example.com",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            # "cpakage=cpakage:main",
            "cpakage=cpakage.main:main",

        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
