from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in pike13/__init__.py
from pike13 import __version__ as version

setup(
	name="pike13",
	version=version,
	description="SowaanERP integration with Pike13",
	author="Sowaan",
	author_email="info@sowaan.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
