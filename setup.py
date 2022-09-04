import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="combinator",
    version="1.1",
    author="Swarna Kamal Paul",
    author_email="swarna.kpaul@gmail.com",
    description="The programming model to integrate AI components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swarna-kpaul/combinator",
    project_urls={
        "Bug Tracker": "https://github.com/swarna-kpaul/combinator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
	keywords = ['programming model', 'dataflow graph', 'functional programming','API integration','Integrative AI'],
	install_requires=[ 'sympy==1.6.2','requests']
)