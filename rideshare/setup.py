from setuptools import setup, find_packages


setup(
    name="rideshare",
    version="0.1.0",
    description="Mobikit Rideshare Example",
    url="https://github.com/mobikitinc/mobikit-examples/tree/master/rideshare",
    packages=find_packages(),
    package_data={"rideshare": ["templates/*"]},
    install_requires=["mobikit~=0.6.0", "Flask~=1.1.1", "Flask-Cors~=3.0.8"],
    entry_points={"console_scripts": ["start-rideshare=rideshare.app:main"]},
)
