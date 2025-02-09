from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent.resolve()
meta = {}
exec((ROOT / "isaac/meta.py").read_text(), meta)
NAME, VERSION, GITHUB = meta["name"], meta["version"], meta["github"]
long_description = (ROOT / "README.md").read_text()


setup(
    name=NAME,
    version=VERSION,
    author="Nitesh Yadav",
    author_email="nitesh.txt@gmail.com",
    description="Cooles locally run AI assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=GITHUB,
    packages=find_packages(),
    install_requires=[
        "yapper-tts",
        "pyreadline3; sys_platform == 'win32'",
        "py-listener",
        "psutil",
        "rich",
    ],
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={
        "console_scripts": [
            "isaac=isaac.cli:main",
        ],
    },
    platforms="Posix; Windows",
    keywords=["AI assistant", "local assistant"],
    python_requires=">=3.9",
)
