#!/usr/bin/env python3
"""
工具模块
提供各种辅助函数
"""

import os
import re
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse
from .compat import safe_filename as _compat_safe_filename


# 支持的平台和 URL 模式
PLATFORM_PATTERNS = {
    'youtube': r'(?:youtube\.com|youtu\.be)',
    'bilibili': r'bilibili\.com',
    'douyin': r'(?:douyin\.com|抖音)',
    'tiktok': r'(?:tiktok\.com)',
    'xiaohongshu': r'xiaohongshu\.com',
    'kuaishou': r'kuaishou\.com',
    'instagram': r'instagram\.com',
    'twitter': r'twitter\.com|x\.com',
    'weixin': r'(?:weixin\.qq\.com|微信)',
    'vimeo': r'vimeo\.com',
    'dailymotion': r'dailymotion\.com',
}


def detect_platform(url: str) -> str:
    """
    检测 URL 所属平台

    Args:
        url: 视频链接

    Returns:
        平台名称
    """
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform

    return 'unknown'


def is_valid_url(url: str) -> bool:
    """
    检查是否为有效的 URL

    Args:
        url: URL 字符串

    Returns:
        是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_urls_from_text(text: str) -> List[str]:
    """
    从文本中提取所有 URL

    Args:
        text: 包含 URL 的文本

    Returns:
        URL 列表
    """
    # URL 正则表达式
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, text)

    # 过滤有效的 URL
    return [url for url in urls if is_valid_url(url)]


def sanitize_filename(filename: str, replace_spaces: bool = True,
                       max_length: int = 255) -> str:
    """
    清理文件名（移除非法字符）

    Args:
        filename: 原始文件名
        replace_spaces: 是否将空格替换为下划线
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    # Delegate to the cross-platform compatibility layer which adds:
    # - Windows reserved name blocking (CON, PRN, AUX, etc.)
    # - Trailing dot/space removal (illegal on Windows)
    # - MAX_PATH awareness
    return _compat_safe_filename(
        filename,
        replace_spaces=replace_spaces,
        max_length=max_length,
    )


def format_filesize(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节大小

    Returns:
        格式化的大小字符串
    """
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024*1024*1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024*1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def format_duration(seconds: int) -> str:
    """
    格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化的时长字符串
    """
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs}s"
    elif seconds >= 60:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        return f"{seconds}s"


def get_video_extensions() -> List[str]:
    """
    获取支持的视频扩展名

    Returns:
        扩展名列表
    """
    return ['mp4', 'mkv', 'webm', 'flv', 'avi', 'mov', 'wmv', 'm4v']


def get_audio_extensions() -> List[str]:
    """
    获取支持的音频扩展名

    Returns:
        扩展名列表
    """
    return ['mp3', 'm4a', 'aac', 'flac', 'wav', 'ogg']


def load_config(config_file: str = "config.json") -> Dict:
    """
    加载配置文件

    Args:
        config_file: 配置文件路径

    Returns:
        配置字典
    """
    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载配置文件失败: {e}")
        return {}


def save_config(config: Dict, config_file: str = "config.json"):
    """
    保存配置文件

    Args:
        config: 配置字典
        config_file: 配置文件路径
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已保存: {config_file}")
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")


def get_output_template(format_option: str = "best") -> str:
    """
    根据格式选项获取输出文件名模板

    Args:
        format_option: 格式选项

    Returns:
        文件名模板
    """
    templates = {
        'best': '%(title)s.%(ext)s',
        'worst': '%(title)s.%(ext)s',
        'mp4': '%(title)s.mp4',
        'webm': '%(title)s.webm',
        'audio-only': '%(title)s.mp3',
    }
    return templates.get(format_option, '%(title)s.%(ext)s')


def check_ffmpeg() -> bool:
    """
    检查是否安装了 ffmpeg

    Returns:
        是否已安装
    """
    import shutil
    return shutil.which('ffmpeg') is not None


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎬  Universal Video Downloader  v1.0.0                ║
║                                                          ║
║   支持: YouTube, Bilibili, 抖音, 快手, 小红书...         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    # 测试工具函数
    print("🔧 工具函数测试:")
    print()

    # 测试 URL 检测
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.bilibili.com/video/BV1xx411s7Z1",
        "https://v.douyin.com/jLd3/",
        "https://www.instagram.com/reel/xxx/",
    ]

    print("URL 平台检测:")
    for url in test_urls:
        platform = detect_platform(url)
        print(f"  {url[:50]:<50} -> {platform}")

    print()

    # 测试文件名清理
    test_names = [
        "My Video: Best Ever!!!.mp4",
        "Test<File/Name>.avi",
        "  spaces  and   multiple   underscores  ",
    ]

    print("文件名清理:")
    for name in test_names:
        clean = sanitize_filename(name)
        print(f"  '{name}' -> '{clean}'")

    print()

    # 测试 URL 提取
    text = """
    这里有几个链接：
    https://www.youtube.com/watch?v=123
    还有这个：https://bilibili.com/video/456
    """

    urls = extract_urls_from_text(text)
    print(f"URL 提取: {urls}")
