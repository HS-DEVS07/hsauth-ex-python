from setuptools import setup, find_packages
import os

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="hsauth",
    version="2.0.0",
    description="Official Python Client SDK for HS DEVS AUTH Licensing & Authentication API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HS DEVS",
    author_email="support@hsdevs.pro",
    url="https://auth.hsdevs.pro",
    project_urls={
        "Documentation": "https://auth.hsdevs.pro/docs",
        "Dashboard": "https://auth.hsdevs.pro/dashboard",
        "Source": "https://github.com/HS-DEVS07/hsauth-ex-python",
    },
    packages=find_packages(),
    py_modules=["hsauth"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[],
)
