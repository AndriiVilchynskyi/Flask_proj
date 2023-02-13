from setuptools import find_packages
from setuptools import setup

setup(
    name="flask_proj",
    version="1.0.0",
    description="This package contains code",
    author="Andrii Vilchynskyi",
    author_email="Fatalist91@gmail.com",
    url="https://github.com/AndriiVilchynskyi/flask_proj",
    packages=find_packages(exclude=("tests*", "testing*")),
)