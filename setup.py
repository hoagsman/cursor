"""
Setup configuration for agent_connectors package.
"""

from setuptools import setup, find_packages

with open("docs/AGENT_CONNECTORS.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agent-connectors",
    version="0.1.0",
    author="Cursor",
    description="Enable agents to connect to Slack and Microsoft Teams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getcursor/cursor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.8.0",
        "slack_sdk>=3.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)
