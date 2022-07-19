import os
import subprocess
import sys

from setuptools import find_packages, setup

try:
    import git
except ModuleNotFoundError:
    subprocess.call([sys.executable, "-m", "pip", "install", "gitpython"])
    import git


with open("requirements.txt") as f:
    required = f.read().splitlines()


# https://stackoverflow.com/questions/56393372/how-to-install-python-package-from-git-repo-that-has-git-lfs-content-with-pip
def pull_first():
    """This script is in a git directory that can be pulled."""
    cwd = os.getcwd()
    gitdir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(gitdir)
    g = git.cmd.Git(gitdir)
    try:
        g.execute(["git", "lfs", "pull"])
    except git.exc.GitCommandError:
        raise RuntimeError("Make sure git-lfs is installed!")
    os.chdir(cwd)


pull_first()

setup(
    name="martello",
    version="1.0",
    description="Martello predictive model",
    author="@CybercentreCanada",
    url="https://github.com/CybercentreCanada/martello/",
    packages=find_packages(),
    package_data={
        "martello": ["bin/libboost_*", "bin/*.bin", "bin/*.pkl"],
    },
    python_requires=">=3.0",
    install_requires=required,
)
