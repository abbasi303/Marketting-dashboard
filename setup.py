from setuptools import setup, find_packages

setup(
    name="marketing-dashboard",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "pandas",
        "numpy",
        "werkzeug",
        "pytest",
        "pytest-cov",
        "flake8",
    ],
)
