"""
Setup configuration for the Aparavi Data Toolchain API SDK.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="dtc-api-sdk",
    version="0.1.0",
    author="Aparavi Software",
    author_email="support@aparavi.com",
    description="Python SDK for the Aparavi Data Toolchain API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aparavi/dtc-api-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Archiving",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dtc-cli=dtc_api_sdk.cli:main",
        ],
    },
    keywords="aparavi data toolchain api sdk automation pipeline",
    project_urls={
        "Bug Reports": "https://github.com/aparavi/dtc-api-sdk/issues",
        "Source": "https://github.com/aparavi/dtc-api-sdk",
        "Documentation": "https://dtc-api-sdk.readthedocs.io/",
    },
) 