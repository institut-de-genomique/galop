import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GALoP",
    version="0.1.0",
    author="Benjamin Istace",
    author_email="bistace@genoscope.cns.fr",
    description="Genome Assembly using Long reads Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"galop": ["workflow/*", "workflow/rules/*", "workflow/profile/*/*"]},
    install_requires=["snakemake", "snakemake-executor-plugin-slurm"],
    entry_points={
        "console_scripts": ["galop=galop.galop:main"],
    },
)