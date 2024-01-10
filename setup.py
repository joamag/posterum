import os
import setuptools

setuptools.setup(
    name="budy",
    version="0.8.5",
    author="Hive Solutions Lda.",
    author_email="development@hive.pt",
    description="Budy E-commerce System",
    license="Apache License, Version 2.0",
    keywords="budy e-commerce engine web json",
    url="http://budy.hive.pt",
    zip_safe=False,
    packages=[
        "budy",
        "budy.controllers",
        "budy.controllers.api",
        "budy.controllers.web",
        "budy.models",
        "budy.test",
    ],
    test_suite="budy.test",
    package_dir={"": os.path.normpath("src")},
    package_data={
        "budy": [
            "static/js/*.js",
            "templates/*.tpl",
            "templates/order/*.tpl",
            "templates/partials/*.tpl",
        ]
    },
    install_requires=["appier", "appier-extras", "commons-py"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md"), "rb")
    .read()
    .decode("utf-8"),
    long_description_content_type="text/markdown",
)
