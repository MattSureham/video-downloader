#!/usr/bin/env python3
"""
批量下载模块
支持从文件、URL列表下载多个视频
"""

import os
import json
import csv
from typing import List, Dict, Optional
from datetime import datetime
from .downloader import VideoDownloader


class BatchDownloader:
    """批量下载管理器"""

    def __init__(self, output_dir: str = "./downloads", cookies_file: Optional[str] = None):
        """
        初始化批量下载器

        Args:
            output_dir: 输出目录
            cookies_file: Cookie 文件路径
        """
        self.output_dir = output_dir
        self.cookies_file = cookies_file
        self.downloader = VideoDownloader(output_dir, cookies_file)

        # 创建日志目录
        self.log_dir = os.path.join(output_dir, ".logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def from_file(self, filepath: str, format_option: str = "best",
                  audio_only: bool = False, max_workers: int = 1) -> Dict:
        """
        从文件批量下载

        Args:
            filepath: 文件路径（支持 .txt, .json, .csv）
            format_option: 视频格式
            audio_only: 是否仅下载音频
            max_workers: 并行数

        Returns:
            下载统计结果
        """
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}

        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.txt':
            urls = self._read_txt(filepath)
        elif ext == '.json':
            urls = self._read_json(filepath)
        elif ext == '.csv':
            urls = self._read_csv(filepath)
        else:
            # 默认尝试 txt
            urls = self._read_txt(filepath)

        if not urls:
            print(f"❌ 文件中没有找到有效的 URL")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}

        print(f"\n📄 从文件读取了 {len(urls)} 个链接")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🎬 格式: {format_option}")
        print(f"🎵 音频模式: {'是' if audio_only else '否'}")

        # 开始下载
        results = self.downloader.download_batch(urls, format_option, audio_only, max_workers)

        # 保存日志
        self._save_log(results, filepath)

        # 统计
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count

        return {
            'success': success_count,
            'failed': fail_count,
            'total': len(results),
            'results': results
        }

    def from_list(self, urls: List[str], format_option: str = "best",
                  audio_only: bool = False) -> Dict:
        """
        从列表批量下载

        Args:
            urls: URL 列表
            format_option: 视频格式
            audio_only: 是否仅下载音频

        Returns:
            下载统计结果
        """
        if not urls:
            print("❌ URL 列表为空")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}

        print(f"\n🚀 开始批量下载 {len(urls)} 个视频")
        print(f"📁 输出目录: {self.output_dir}")

        results = self.downloader.download_batch(urls, format_option, audio_only)

        # 统计
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count

        return {
            'success': success_count,
            'failed': fail_count,
            'total': len(results),
            'results': results
        }

    def resume_from_log(self, log_filepath: str, format_option: str = "best",
                         audio_only: bool = False) -> Dict:
        """
        从日志文件恢复下载（仅下载失败的）

        Args:
            log_filepath: 日志文件路径
            format_option: 视频格式
            audio_only: 是否仅下载音频

        Returns:
            下载统计结果
        """
        if not os.path.exists(log_filepath):
            print(f"❌ 日志文件不存在: {log_filepath}")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}

        # 读取失败的 URL
        failed_urls = []
        with open(log_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if not data.get('success', False):
                        failed_urls.append(data.get('url', ''))
                except:
                    continue

        if not failed_urls:
            print("✅ 没有失败的下载需要恢复")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}

        print(f"\n🔄 恢复 {len(failed_urls)} 个失败的下载...")

        results = self.downloader.download_batch(failed_urls, format_option, audio_only)

        # 合并结果
        return {
            'success': sum(1 for r in results if r['success']),
            'failed': len(results) - sum(1 for r in results if r['success']),
            'total': len(results),
            'results': results
        }

    def _read_txt(self, filepath: str) -> List[str]:
        """读取 txt 文件（每行一个 URL）"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls

    def _read_json(self, filepath: str) -> List[str]:
        """读取 JSON 文件"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 支持多种 JSON 格式
            if isinstance(data, list):
                urls = [item if isinstance(item, str) else item.get('url', '') for item in data]
            elif isinstance(data, dict):
                urls = data.get('urls', data.get('links', []))
                if isinstance(urls, str):
                    urls = [urls]

        return [u for u in urls if u]

    def _read_csv(self, filepath: str) -> List[str]:
        """读取 CSV 文件"""
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 尝试多种可能的列名
                url = row.get('url', row.get('link', row.get('URL', '')))
                if url:
                    urls.append(url)

        return urls

    def _save_log(self, results: List[Dict], source_file: str):
        """保存下载日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"download_log_{timestamp}.jsonl")

        with open(log_file, 'w', encoding='utf-8') as f:
            for result in results:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'source': source_file,
                    **result
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        print(f"\n📝 下载日志已保存: {log_file}")


if __name__ == "__main__":
    # 测试批量下载
    import sys

    if len(sys.argv) < 2:
        print("用法: python batch.py <链接文件>")
        sys.exit(1)

    batch = BatchDownloader("./downloads")
    result = batch.from_file(sys.argv[1])

    print(f"\n📊 下载完成:")
    print(f"  ✅ 成功: {result['success']}")
    print(f"  ❌ 失败: {result['failed']}")
    print(f"  📁 总计: {result['total']}")
