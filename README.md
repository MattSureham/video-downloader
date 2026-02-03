# 🎬 Universal Video Downloader

通用视频下载器 - 支持抖音、微信短视频、Bilibili、YouTube、快手、小红书等平台！

## ✨ Features

- ✅ **多平台支持** - 抖音、微信短视频、Bilibili、YouTube、快手、小红书等
- ✅ **单个下载** - 输入链接即可下载
- ✅ **批量下载** - 支持从文件读取链接列表
- ✅ **多种格式** - 支持视频、音频提取
- ✅ **简洁CLI** - 简单易用的命令行界面

## 🚀 Quick Start

### 安装

```bash
# 克隆项目
git clone https://github.com/MattSureham/video-downloader.git
cd video-downloader

# 安装依赖
pip install -r requirements.txt

# 安装 yt-dlp（必须）
pip install yt-dlp

# 可选：安装 ffmpeg（用于格式转换）
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
# Windows: 下载并添加到 PATH
```

### 使用方法

#### 单个视频下载

```bash
python -m video_downloader "https://www.youtube.com/watch?v=..."
python -m video_downloader "https://www.bilibili.com/video/BV1xx..."
python -m video_downloader "https://v.douyin.com/..."
```

#### 批量下载

```bash
# 从文件读取链接（每行一个链接）
python -m video_downloader --batch links.txt

# 指定输出目录
python -m video_downloader --batch links.txt --output ~/Downloads/videos

# 下载音频 only
python -m video_downloader --batch links.txt --audio-only
```

#### 交互模式

```bash
python -m video_downloader --interactive
```

## 📖 使用示例

```bash
# 下载单个视频
$ python -m video_downloader "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 下载并选择格式
$ python -m video_downloader "https://www.bilibili.com/video/BV1xx411s7Z1" --format best

# 批量下载
$ python -m video_downloader --batch my_videos.txt

# 下载音频
$ python -m video_downloader "https://www.youtube.com/watch?v=..." --audio-only

# 指定下载路径
$ python -m video_downloader "https://..." --output /path/to/folder
```

## 🛠️ CLI 参数

```
positional arguments:
  url                   视频链接（单个下载模式）

optional arguments:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        下载目录（默认: ./downloads）
  -f FORMAT, --format FORMAT
                        视频格式: best, worst, mp4, webm, audio-only
  -b, --batch           批量下载模式（从文件读取链接）
  -i, --interactive    交互模式
  --audio-only         仅下载音频
  --playlist          下载整个播放列表
  --verbose            显示详细输出
  --cookies COOKIES   Cookie 文件（用于需要登录的平台）
```

## 📦 支持的平台

| 平台 | 状态 | 备注 |
|------|------|------|
| YouTube | ✅ 完全支持 |  |
| Bilibili | ✅ 完全支持 |  |
| 抖音 | ✅ 完全支持 |  |
| 快手 | ✅ 完全支持 |  |
| 小红书 | ✅ 完全支持 |  |
| 微信短视频 | ✅ 完全支持 |  |
| Instagram | ✅ 完全支持 | Reels, Posts |
| Twitter/X | ✅ 完全支持 |  |
| TikTok | ✅ 完全支持 |  |

## 🔧 高级用法

### 使用 Cookie 下载需要登录的视频

```bash
# 导出浏览器 Cookie（需要 Chrome 扩展）
# 安装 Get cookies.txt: https://chrome.google.com/webstore/detail/get-cookiestxt

# 使用 Cookie 文件
python -m video_downloader "https://..." --cookies cookies.txt
```

### 下载整个播放列表

```bash
python -m video_downloader "https://www.youtube.com/playlist?list=..." --playlist
```

### 自定义文件名模板

```bash
python -m video_downloader "https://..." -o "./downloads/%(title)s.%(ext)s"
```

## 📁 项目结构

```
video-downloader/
├── README.md
├── requirements.txt
├── setup.py
├── video_downloader/
│   ├── __init__.py
│   ├── __version__.py
│   ├── downloader.py      # 核心下载逻辑
│   ├── cli.py             # 命令行界面
│   ├── batch.py           # 批量下载
│   ├── platforms.py       # 平台支持
│   └── utils.py           # 工具函数
├── tests/
│   └── __init__.py
├── examples/
│   └── links_examples.txt
└── docs/
    └── README_CN.md
```

## 🤝 贡献

欢迎贡献代码！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载核心

## 📧 联系

- GitHub: [@MattSureham](https://github.com/MattSureham)
- Email: surehamhuang@gmail.com

---

**Happy Downloading!** 🎬✨
