"""
Universal Video Downloader
通用视频下载器 - 支持多个平台的视频下载
"""

__version__ = "1.0.0"
__author__ = "Matt Sureham"
__email__ = "surehamhuang@gmail.com"

from .downloader import VideoDownloader
from .cli import main

__all__ = ['VideoDownloader', 'main']
