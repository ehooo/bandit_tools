# -*- coding: utf-8 -*-
"""
Copyright 2019 Victor Torre

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="bandit_tools",
    version="0.0.1",
    author="Victor Torre",
    author_email="web.ehooo@gmail.com",
    description="Basic Tools for improve Bandit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehooo/bandit_tools/",
    keywords=['testing', 'security', 'bandit'],
    packages=setuptools.find_packages(),
    license="Apache 2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Security",
    ],
    install_requires=["jinja2", "bandit"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "baseline_tools=bandit_tools.baseline_tools:main",
            "bandit_custom_report=bandit_tools.custom_report:main",
        ]
    },
)
