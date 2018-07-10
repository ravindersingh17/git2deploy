#!/usr/bin/env python3
#Added comment
from setuptools import setup

setup(
        name="git2deploy",
        version="1.0",
        description="Deploy software from git to dir",
        author="Ravinder Singh",
        author_email="ravinder.ssgh@gmail.com",
        url="https://github.com/ravindersingh17/git2deploy",
        python_requires=">=3",
        packages=["g2d"],
        scripts=["bin/g2d"],
        data_files=[("/var/www/html/", ["php/webhook.php"]),
            ("/usr/lib/systemd/system/", ["service/git2deploy.service"])],
        )

