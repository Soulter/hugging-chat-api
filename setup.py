from setuptools import find_namespace_packages
from setuptools import setup

setup(
    name="hugchat",
    version="0.4.11",
    description="A huggingchat python api.",
    long_description=open("README.md", "rt", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Soulter/hugging-chat-api",
    project_urls={
        "Bug Report": "https://github.com/Soulter/hugging-chat-api/issues"
    },
    author="Soulter",
    author_email="905617992@qq.com",
    license="GNU Affero General Public License v3.0",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    py_modules=["hugchat"],
    package_data={"": ["*.json"]},
    install_requires=[
        "requests",
        "requests_toolbelt",
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
