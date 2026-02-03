#!/usr/bin/env python3
"""
命令行界面模块
提供简洁易用的命令行操作
"""

import argparse
import sys
import os
from .downloader import VideoDownloader


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="🎬 Universal Video Downloader - 通用视频下载器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "https://www.youtube.com/watch?v=..."           # 下载单个视频
  %(prog)s "https://www.bilibili.com/video/BV1xx..."      # 下载B站视频
  %(prog)s -b links.txt                                   # 批量下载
  %(prog)s -b links.txt --audio-only                      # 批量下载音频
  %(prog)s --info "https://..."                            # 查看视频信息
  %(prog)s --list-formats "https://..."                    # 列出可用格式

支持的平台:
  YouTube, Bilibili, 抖音, 快手, 小红书, 微信短视频, Instagram, Twitter等
        """
    )

    # 必需参数
    parser.add_argument(
        'url',
        nargs='?',
        help='视频链接（单个下载模式）'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        default='./downloads',
        help='下载目录（默认: ./downloads）'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['best', 'worst', 'mp4', 'webm', 'audio-only'],
        default='best',
        help='视频格式（默认: best）'
    )

    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='批量下载模式（从文件读取链接）'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='交互模式'
    )

    parser.add_argument(
        '--audio-only',
        action='store_true',
        help='仅下载音频（MP3格式）'
    )

    parser.add_argument(
        '--playlist',
        action='store_true',
        help='下载整个播放列表'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='仅显示视频信息，不下载'
    )

    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='列出所有可用格式'
    )

    parser.add_argument(
        '--cookies',
        default=None,
        help='Cookie文件路径（用于需要登录的视频）'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser


def print_video_info(info: dict):
    """打印视频信息"""
    if not info:
        print("❌ 无法获取视频信息")
        return

    print("\n" + "=" * 60)
    print("🎬 视频信息")
    print("=" * 60)
    print(f"📌 标题: {info.get('title', 'Unknown')}")
    print(f"👤 作者: {info.get('uploader', 'Unknown')}")
    print(f"⏱️  时长: {info.get('duration', 0)} 秒")

    duration = info.get('duration', 0)
    if duration:
        mins = duration // 60
        secs = duration % 60
        print(f"           ({mins}分{secs}秒)")

    print(f"👁️  播放量: {info.get('view_count', 0):,}")
    print(f"📅 上传日期: {info.get('upload_date', 'Unknown')}")
    print(f"🔗 链接: {info.get('url', 'Unknown')}")

    if info.get('thumbnail'):
        print(f"🖼️  封面: {info['thumbnail']}")

    description = info.get('description', '')
    if description:
        print(f"\n📝 简介（前500字符）:")
        print("-" * 60)
        print(description[:500])
        if len(description) > 500:
            print("...")

    print("=" * 60 + "\n")


def print_formats(formats: list):
    """打印可用格式列表"""
    if not formats:
        print("❌ 无法获取格式列表")
        return

    print("\n📋 可用格式:")
    print("-" * 80)
    print(f"{'ID':<6} {'扩展名':<8} {'分辨率':<15} {'大小':<12} {'备注'}")
    print("-" * 80)

    for f in formats:
        format_id = f.get('format_id', '-')
        ext = f.get('ext', '-')
        resolution = f.get('resolution', '-')
        filesize = f.get('filesize', 0)
        format_note = f.get('format_note', '')

        if filesize:
            if filesize > 1024 * 1024 * 1024:
                size_str = f"{filesize / (1024*1024*1024):.1f} GB"
            elif filesize > 1024 * 1024:
                size_str = f"{filesize / (1024*1024):.1f} MB"
            else:
                size_str = f"{filesize / 1024:.1f} KB"
        else:
            size_str = "Unknown"

        print(f"{format_id:<6} {ext:<8} {resolution:<15} {size_str:<12} {format_note}")

    print("-" * 80 + "\n")


def read_urls_from_file(filepath: str) -> list:
    """从文件读取URL列表"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return []

    urls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 忽略空行和注释
            if line and not line.startswith('#'):
                urls.append(line)

    return urls


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    # 交互模式
    if args.interactive:
        print("\n🎬 欢迎使用 Universal Video Downloader!")
        print("输入 'quit' 或 'exit' 退出\n")

        downloader = VideoDownloader(args.output, args.cookies)

        while True:
            try:
                url = input("请输入视频链接: ").strip()

                if url.lower() in ['quit', 'exit', 'q', '退出']:
                    print("👋 再见!")
                    break

                if not url:
                    continue

                # 查看信息
                info = downloader.get_video_info(url)
                if info:
                    print_video_info(info)

                    choice = input("下载这个视频? (y/n): ").strip().lower()
                    if choice in ['y', 'yes', '是']:
                        result = downloader.download(
                            url,
                            format_option=args.format,
                            audio_only=args.audio_only
                        )
                        if result['success']:
                            print(f"✅ 下载成功: {result.get('title', 'Unknown')}")
                        else:
                            print(f"❌ 下载失败: {result.get('error', 'Unknown error')}")
                else:
                    print("❌ 无法获取视频信息")

            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

        return 0

    # 检查必需参数
    if not args.url and not args.batch:
        parser.print_help()
        print("\n❌ 请提供视频链接或使用 --batch 指定链接文件")
        return 1

    # 批量模式
    if args.batch:
        if not args.url:
            print("❌ 请指定链接文件")
            return 1

        urls = read_urls_from_file(args.url)
        if not urls:
            print("❌ 文件中没有有效的链接")
            return 1

        print(f"📄 从文件读取了 {len(urls)} 个链接")

        downloader = VideoDownloader(args.output, args.cookies)
        results = downloader.download_batch(
            urls,
            format_option=args.format,
            audio_only=args.audio_only
        )

        # 返回适当的退出码
        success_count = sum(1 for r in results if r['success'])
        return 0 if success_count == len(urls) else 1

    # 单个视频模式
    url = args.url

    # 查看信息模式
    if args.info:
        downloader = VideoDownloader(args.output, args.cookies)
        info = downloader.get_video_info(url)
        print_video_info(info)
        return 0

    # 列出格式模式
    if args.list_formats:
        downloader = VideoDownloader(args.output, args.cookies)
        formats = downloader.list_formats(url)
        print_formats(formats)
        return 0

    # 下载模式
    downloader = VideoDownloader(args.output, args.cookies)

    # 获取并显示信息
    info = downloader.get_video_info(url)
    if info and not args.verbose:
        print_video_info(info)

    # 下载
    print(f"\n🚀 开始下载...")
    result = downloader.download(
        url,
        format_option=args.format,
        audio_only=args.audio_only
    )

    if result['success']:
        print(f"\n✅ 下载成功!")
        print(f"📁 文件位置: {result.get('filepath', 'Unknown')}")
        return 0
    else:
        print(f"\n❌ 下载失败: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
