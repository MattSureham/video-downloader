"""
核心下载器模块
支持多个平台的视频下载
"""

import os
import yt_dlp
from typing import Optional, Dict, List, Callable
from tqdm import tqdm
import colorama
from .compat import normalize_output_path, safe_filename


class VideoDownloader:
    """视频下载器类"""

    def __init__(self, output_dir: str = "./downloads", cookies_file: Optional[str] = None):
        """
        初始化下载器

        Args:
            output_dir: 下载目录
            cookies_file: Cookie 文件路径（用于需要登录的视频）
        """
        self.output_dir = output_dir
        self.cookies_file = cookies_file
        self.progress_hook = None

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

    def set_progress_hook(self, hook: Callable):
        """设置进度回调函数"""
        self.progress_hook = hook

    def _get_ydl_options(self, format_option: str = "best", audio_only: bool = False) -> Dict:
        """
        获取 yt-dlp 选项

        Args:
            format_option: 格式选项
            audio_only: 是否仅下载音频

        Returns:
            yt-dlp 选项字典
        """
        options = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [],
            'quiet': False,
            'no_warnings': False,
        }

        # Capture the actual output filename after post-processing
        self._last_downloaded_file = None

        def _capture_filename(d):
            if d.get('status') == 'finished':
                self._last_downloaded_file = d.get('filename')

        options['progress_hooks'].append(_capture_filename)

        # 添加进度回调
        if self.progress_hook:
            options['progress_hooks'].append(self.progress_hook)

        # Cookie 支持
        if self.cookies_file and os.path.exists(self.cookies_file):
            options['cookiefile'] = self.cookies_file

        # 格式选择
        if audio_only:
            options['format'] = 'bestaudio[ext=m4a]/bestaudio'
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if format_option == "best":
                options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif format_option == "worst":
                options['format'] = 'worstvideo[ext=mp4]+worstaudio/worst[ext=mp4]/worst'
            elif format_option == "mp4":
                options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
            elif format_option == "webm":
                options['format'] = 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]'

        return options

    def download(self, url: str, format_option: str = "best", audio_only: bool = False) -> Dict:
        """
        下载单个视频

        Args:
            url: 视频链接
            format_option: 格式选项
            audio_only: 是否仅下载音频

        Returns:
            下载结果字典
        """
        options = self._get_ydl_options(format_option, audio_only)

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                # 获取视频信息
                info = ydl.extract_info(url, download=False)

                # 下载视频
                ydl.download([url])

                # Use the actual post-processing filename captured by the hook,
                # not the pre-download guess (ffmpeg merging can change extension)
                filepath = self._last_downloaded_file
                if not filepath:
                    # Fallback: use prepare_filename for the pre-download guess
                    filepath = ydl.prepare_filename(info)
                filepath = normalize_output_path(self.output_dir,
                                                 os.path.basename(filepath))

                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'url': url,
                    'format': format_option,
                    'audio_only': audio_only,
                    'filepath': filepath,
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

    def download_batch(self, urls: List[str], format_option: str = "best",
                       audio_only: bool = False, max_workers: int = 1) -> List[Dict]:
        """
        批量下载视频

        Args:
            urls: 视频链接列表
            format_option: 格式选项
            audio_only: 是否仅下载音频
            max_workers: 并行下载数（目前只支持1）

        Returns:
            下载结果列表
        """
        results = []
        total = len(urls)

        print(f"\n🚀 开始下载 {total} 个视频...")
        print(f"📁 输出目录: {self.output_dir}\n")

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{total}] 下载中: {url}")

            # 创建带进度的回调
            pbar = None

            def progress_hook(d):
                if d['status'] == 'downloading':
                    if pbar is None:
                        pbar = tqdm(total=100, desc="下载中", unit="%")
                    percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                    pbar.update(percent - pbar.n)
                elif d['status'] == 'finished':
                    if pbar:
                        pbar.close()
                    print(f"✅ 下载完成: {d.get('filename', 'unknown')}")

            self.set_progress_hook(progress_hook)

            result = self.download(url, format_option, audio_only)
            results.append(result)

            if result['success']:
                print(f"✅ 成功: {result.get('title', 'Unknown')}")
            else:
                print(f"❌ 失败: {result.get('error', 'Unknown error')}")

        # 统计
        success_count = sum(1 for r in results if r['success'])
        fail_count = total - success_count

        print(f"\n📊 下载统计:")
        print(f"  ✅ 成功: {success_count}")
        print(f"  ❌ 失败: {fail_count}")
        print(f"  📁 总计: {total}")

        return results

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        获取视频信息（不下载）

        Args:
            url: 视频链接

        Returns:
            视频信息字典
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'formats': info.get('formats', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:500],
                    'url': url
                }
        except Exception as e:
            print(f"❌ 获取信息失败: {e}")
            return None

    def list_formats(self, url: str) -> List[Dict]:
        """
        列出可用格式

        Args:
            url: 视频链接

        Returns:
            格式列表
        """
        info = self.get_video_info(url)
        if info:
            formats = info.get('formats', [])
            return [
                {
                    'format_id': f.get('format_id', ''),
                    'ext': f.get('ext', ''),
                    'resolution': f.get('resolution', 'Unknown'),
                    'filesize': f.get('filesize', 0),
                    'format_note': f.get('format_note', '')
                }
                for f in formats
            ]
        return []

    def download_by_format_id(self, url: str, format_id: str) -> Dict:
        """
        按 format_id 下载特定格式

        Args:
            url: 视频链接
            format_id: 格式 ID

        Returns:
            下载结果
        """
        options = self._get_ydl_options()
        options['format'] = format_id

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                ydl.download([url])

                # Capture actual filepath from the progress hook
                filepath = self._last_downloaded_file
                if not filepath:
                    filepath = ydl.prepare_filename(info)
                filepath = normalize_output_path(self.output_dir,
                                                 os.path.basename(filepath))

                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'format_id': format_id,
                    'filepath': filepath,
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == "__main__":
    # 测试下载器
    downloader = VideoDownloader("./test_downloads")

    # 测试获取信息
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll 😄
    info = downloader.get_video_info(test_url)

    if info:
        print(f"\n🎬 视频信息:")
        print(f"  标题: {info['title']}")
        print(f"  作者: {info['uploader']}")
        print(f"  时长: {info['duration']} 秒")
        print(f"  播放量: {info['view_count']}")
