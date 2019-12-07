import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="github_cli",
    version="0.0.1",
    author="Karunakaran Prasad",
    author_email="karunakaran.prasad@gmail.com",
    description="Package demonstrating getting top N repos of an organization by various criteria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/knair99/github_cli",
    # packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=['github_cli'],
    entry_points={
        'console_scripts': [
            'github_cli = github_cli.__main__:main'
        ]}
)
