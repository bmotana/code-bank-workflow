from setuptools import find_packages, setup

setup(
    name="code-bank-workflow",
    version="0.1.0",
    description="Learning system for mastering code snippets through structured practice",
    author="Bafana Motana",
    license="MIT",
    packages=find_packages(include=["src", "src.*", "config", "config.*"]),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "python-dotenv",
        "PyYAML",
        "pygments",
    ],
    extras_require={
        "dev": [
            "flake8",
            "flake8-annotations",
            "flake8-bugbear",
            "flake8-docstrings",
            "flake8-import-order",
            "pytest",
        ],
    },
    include_package_data=True,
)
