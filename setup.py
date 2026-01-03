from setuptools import setup, find_packages
from pathlib import Path

# 读取README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="contract-auditor",
    version="1.0.0",
    description="智能合约安全审计工具",
    author="tr3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'contract_auditor': [
            'reporter/templates/*.html',
        ],
    },
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

