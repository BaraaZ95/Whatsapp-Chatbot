from setuptools import setup, find_packages

setup(
    name="Whatsapp_hatbot",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["gunicorn" "Flask", "Flask-PyMongo", "mongomock"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
