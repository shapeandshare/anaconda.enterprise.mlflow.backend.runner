import setuptools
from setuptools import setup

setup(
    name="anaconda.enterprise.mlflow.backend.runner",
    version="0.0.1",
    description=" MLFlow Backend For Anaconda Enterprise",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    author="Joshua C. Burt"
)
