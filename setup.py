import os
import setuptools

setuptools.setup(
    name="posterum",
    version="0.1.1",
    author="João Magalhães",
    author_email="joamag@gmail.com",
    description="Simple e-mail address SMTP verification service",
    license="Apache License, Version 2.0",
    keywords="post smtp validation",
    url="https://posterum.bemisc.com",
    zip_safe=False,
    packages=["posterum", "posterum.controllers", "posterum.common"],
    test_suite="posterum.test",
    package_dir={"": os.path.normpath("src")},
    install_requires=["appier", "appier-extras", "jinja2", "fastapi"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md"), "rb")
    .read()
    .decode("utf-8"),
    long_description_content_type="text/markdown",
)
