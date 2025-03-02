from setuptools import setup, find_packages

setup(
    name="teso",
    version="0.1.0",
    description="Tabu‐Enhanced Simulation Optimization (TESO) package, combining simulation optimization with tabu search and memory strategies.",
    author="Bulent Soykan",
    author_email="soykanb@gmail.com",
    url="https://github.com/bulentsoykan/teso",  
    packages=find_packages(),  
    install_requires=[
        "numpy",
        "mrg32k3a",
        "simopt",  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)