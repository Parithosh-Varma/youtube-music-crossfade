from setuptools import setup, find_packages

setup(
    name="ytcrossfade",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "yt-dlp>=2024",
        "pydub>=0.25",
    ],
    entry_points={
        "console_scripts": [
            "ytcrossfade=ytcrossfade.cli:main",
        ],
    },
    python_requires=">=3.8",
)
