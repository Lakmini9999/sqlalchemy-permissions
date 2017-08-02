"""
A simple permissions system for developers using SQLAlchemy.
"""
from setuptools import setup


setup(
    name="SQLAlchemy-Permissions",
    version="0.1.0",
    url="https://github.com/LouisTrezzini/sqlalchemy-permissions",
    license="MIT",
    author="Louis Trezzini",
    author_email="louis.trezzini@ponts.org",
    description="Simple user permissions for SQLAlchemy",
    long_description=__doc__,
    packages=["sqlalchemy_permissions"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "SQLAlchemy"
    ],
    classifiers=[
        "Framework :: Flask",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
