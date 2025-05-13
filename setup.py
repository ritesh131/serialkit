from setuptools import setup, find_packages

setup(
    name="serialkit",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.5",
    ],
    author="Ritesh Bajpai",
    author_email="bajpairitesh878@gmail.com",
    description="A Python toolkit for serial and USB communication with dynamic configuration and command support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ritesh131/serialkit",
    license="Proprietary",
    classifiers=[
           "Programming Language :: Python :: 3",
           "License :: Other/Proprietary License",
           "Operating System :: OS Independent",
       ],
       python_requires=">=3.6",
)