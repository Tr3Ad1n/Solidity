from setuptools import setup, find_packages

setup(
    name="contract-auditor",
    version="1.0.0",
    description="智能合约安全审计工具",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pygments>=2.15.0",
        "jinja2>=3.1.2",
        "networkx>=3.1",
        "click>=8.1.7",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "contract-auditor=contract_auditor.main:main",
        ],
    },
    python_requires=">=3.11",
)

