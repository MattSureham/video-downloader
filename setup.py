#!/usr/bin/env python3
"""
安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="universal-video-downloader",
    version="1.0.0",
    author="Matt Sureham",
    author_email="surehamhuang@gmail.com",
    description="Universal Video Downloader - Support YouTube, Bilibili, Douyin, and more!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MattSureham/video-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords=[
        "video", "downloader", "youtube", "bilibili", "douyin",
        "tiktok", "instagram", "twitter", "cli", "tool"
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.9.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ],
        "gui": [
            "PyQt5>=5.15.10",
        ],
    },
    entry_points={
        "console_scripts": [
            "video-downloader=video_downloader.cli:main",
            "vd=video_downloader.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "video_downloader": ["*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/MattSureham/video-downloader/issues",
        "Source": "https://github.com/MattSureham/video-downloader",
        "Documentation": "https://github.com/MattSureham/video-downloader#readme",
    },
)
