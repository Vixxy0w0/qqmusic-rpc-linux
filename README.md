<div align="center">

# QQ Music & NetEase Cloud Music Discord RPC (Linux)

[![English](https://img.shields.io/badge/README-English-blue)](#english)
[![简体中文](https://img.shields.io/badge/README-简体中文-red)](#简体中文)

<div align="center">

<table>
<tr>
<td><img src="https://github.com/user-attachments/assets/43b5762a-58ed-4134-bcd0-7dde65dacc0a" width="350"/></td>
<td><img src="https://github.com/user-attachments/assets/135574da-99e1-49e7-8a5b-d45b6f15bf4e" width="350"/></td>
</tr>
<tr>
<td align="center">QQ Music | QQ 音乐</td>
<td align="center">NetEase Cloud Music | 网易云音乐</td>
</tr>
</table>

</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
![Platform: Linux](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)

</div>

---

<a name="english"></a>
# 🇬🇧 English

> Discord Rich Presence for QQ Music and NetEase Cloud Music on Linux — shows your current track, artist, album art, and playback state. Automatically detects which player is active and switches presence accordingly.

## Supported Players

| Player | Album Art Source | Flatpak |
|---|---|---|
| QQ Music (official Linux build) | iTunes Search API | No |
| NetEase Cloud Music Gtk4 | MPRIS metadata (direct) | Yes |

## Features

- **Multi-player support** — detects QQ Music and NetEase Cloud Music Gtk4, switches Discord presence automatically when you switch players
- **Album art** — fetched via iTunes for QQ Music; pulled directly from the player for NetEase
- **Smart player detection** — uses MPRIS (D-Bus) with behavioral filtering to distinguish music players from browsers, even when both identify as Chromium
- **Isolated install** — uses a Python venv, no sudo, no system package conflicts
- **Auto-start** — runs as a systemd user service that starts on login
- **One-command updates** — `./install.sh --update`

## Requirements

- Linux (any distro with systemd)
- Python 3.8+
- `python3-venv` (see below if missing)
- Discord desktop app (not browser)
- QQ Music and/or NetEase Cloud Music Gtk4

## Installation

```bash
git clone https://github.com/Vixxy0w0/qqmusic-rpc-linux.git
cd qqmusic-rpc-linux
chmod +x install.sh
./install.sh
```

The installer will:
1. Create an isolated Python venv at `~/.local/share/qqmusic-rpc/venv`
2. Install dependencies into it
3. Register and start a systemd user service
4. Create a `qqmusic-rpc` command in `~/.local/bin`

**The service starts automatically on login from this point forward.**

### Missing `python3-venv`?

| Distro | Command |
|---|---|
| Ubuntu / Debian | `sudo apt install python3-venv` |
| Arch / CachyOS / Manjaro | `sudo pacman -S python` |
| Fedora | `sudo dnf install python3` |

## Updating

From inside the cloned repo:

```bash
./install.sh --update
```

## Controls

| Action | Command |
|---|---|
| View logs (live) | `journalctl --user -u qqmusic-rpc -f` |
| Restart service | `systemctl --user restart qqmusic-rpc` |
| Stop service | `systemctl --user stop qqmusic-rpc` |
| Start service | `systemctl --user start qqmusic-rpc` |

## Uninstall

```bash
systemctl --user stop qqmusic-rpc
systemctl --user disable qqmusic-rpc
rm ~/.config/systemd/user/qqmusic-rpc.service
rm ~/.local/bin/qqmusic-rpc
rm -rf ~/.local/share/qqmusic-rpc
systemctl --user daemon-reload
```

## Troubleshooting

**Presence not showing in Discord**
- Open Discord Settings → Activity Privacy → enable "Share your detected activities"
- Make sure a song is actually playing (not paused)
- Check logs: `journalctl --user -u qqmusic-rpc -f`

**Album art not loading**
- For QQ Music, art depends on iTunes availability — obscure or China-exclusive tracks may not be found and will fall back to the player logo
- For NetEase, art is pulled directly from the app — if it's missing, the app itself isn't exposing it
- Check your internet connection if no art is loading at all

**Service crashes on startup**
- Run `journalctl --user -u qqmusic-rpc -n 30 --no-pager` and check the error
- Make sure Discord is open before or shortly after the service starts

**Works manually but not as a service**
- Make sure `~/.local/bin` is in your `$PATH`. Add this to `~/.bashrc` or `~/.zshrc`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

## How it works

The script polls the session D-Bus every 5 seconds using the [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) interface (`org.mpris.MediaPlayer2`). It identifies the active player by its MPRIS identity string and uses behavioral checks (next/previous track support) to filter out browsers that also expose MPRIS. QQ Music runs as an Electron app and identifies itself as Chromium on D-Bus, so this behavioral check is what distinguishes it from actual browsers.

Each supported player has its own Discord application, so the correct logo and app name shows in Discord automatically when you switch players.

## Changelog

See [Releases](https://github.com/Vixxy0w0/qqmusic-rpc-linux/releases) for version history.

## License

[MIT](LICENSE)

---

<a name="简体中文"></a>
# 🇨🇳 简体中文

> 在 Linux 上为 QQ 音乐和网易云音乐实现 Discord 状态同步，显示当前播放的歌曲、歌手、专辑封面及播放状态。自动检测当前活跃的播放器并切换对应的 Discord 状态。

## 支持的播放器

| 播放器 | 专辑封面来源 | Flatpak |
|---|---|---|
| QQ 音乐（官方 Linux 版） | iTunes Search API | 否 |
| 网易云音乐 Gtk4 | MPRIS 元数据（直接读取） | 是 |

## 功能特点

- **多播放器支持** — 自动检测 QQ 音乐和网易云音乐 Gtk4，切换播放器时自动更新 Discord 状态
- **专辑封面** — QQ 音乐通过 iTunes 获取封面；网易云直接从播放器读取
- **智能识别播放器** — 通过 MPRIS（D-Bus）及行为特征过滤，即使播放器以 Chromium 身份注册也能与浏览器区分
- **纯净安装** — 使用 Python 虚拟环境，无需 sudo，不污染系统包
- **开机自启** — 以 systemd 用户服务运行，登录后自动启动
- **一键更新** — `./install.sh --update`

## 运行要求

- Linux（任意带有 systemd 的发行版）
- Python 3.8 及以上
- `python3-venv`（缺失时见下方说明）
- Discord 桌面客户端（不支持网页版）
- QQ 音乐 和/或 网易云音乐 Gtk4

## 安装方法

```bash
git clone https://github.com/Vixxy0w0/qqmusic-rpc-linux.git
cd qqmusic-rpc-linux
chmod +x install.sh
./install.sh
```

安装脚本将自动完成以下操作：
1. 在 `~/.local/share/qqmusic-rpc/venv` 创建隔离的 Python 虚拟环境
2. 在虚拟环境中安装所有依赖
3. 注册并启动 systemd 用户服务
4. 在 `~/.local/bin` 创建 `qqmusic-rpc` 快捷命令

**安装完成后，每次登录系统服务将自动启动。**

### 缺少 `python3-venv`？

| 发行版 | 安装命令 |
|---|---|
| Ubuntu / Debian | `sudo apt install python3-venv` |
| Arch / CachyOS / Manjaro | `sudo pacman -S python` |
| Fedora | `sudo dnf install python3` |

## 更新方法

在已克隆的项目目录中执行：

```bash
./install.sh --update
```

## 常用命令

| 操作 | 命令 |
|---|---|
| 实时查看日志 | `journalctl --user -u qqmusic-rpc -f` |
| 重启服务 | `systemctl --user restart qqmusic-rpc` |
| 停止服务 | `systemctl --user stop qqmusic-rpc` |
| 启动服务 | `systemctl --user start qqmusic-rpc` |

## 卸载

```bash
systemctl --user stop qqmusic-rpc
systemctl --user disable qqmusic-rpc
rm ~/.config/systemd/user/qqmusic-rpc.service
rm ~/.local/bin/qqmusic-rpc
rm -rf ~/.local/share/qqmusic-rpc
systemctl --user daemon-reload
```

## 常见问题

**Discord 没有显示状态**
- 打开 Discord 设置 → 活动隐私 → 启用"分享检测到的活动"
- 确保正在播放歌曲（非暂停状态）
- 查看日志：`journalctl --user -u qqmusic-rpc -f`

**封面不显示**
- QQ 音乐封面依赖 iTunes 数据，冷门或中国独占曲目可能无法获取，会自动回退显示播放器图标
- 网易云封面直接从应用读取，若缺失说明应用本身未提供封面数据
- 若所有歌曲均无封面，请检查网络连接

**服务启动崩溃**
- 运行 `journalctl --user -u qqmusic-rpc -n 30 --no-pager` 查看错误信息
- 确保 Discord 已在服务启动前或启动后不久打开

**手动运行正常，但服务不工作**
- 确认 `~/.local/bin` 在 `$PATH` 中。将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

## 工作原理

脚本每 5 秒通过 [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) 接口（`org.mpris.MediaPlayer2`）轮询 D-Bus 会话总线。通过 MPRIS 身份字符串识别当前活跃的播放器，并结合行为特征（是否支持切换曲目）过滤掉同样暴露 MPRIS 接口的浏览器。QQ 音乐基于 Electron，在 D-Bus 上以 Chromium 身份注册，因此行为检测是区分它与真实浏览器的关键。

每个支持的播放器对应独立的 Discord 应用，切换播放器时 Discord 会自动显示对应的图标和应用名称。

## 更新日志

版本历史请查看 [Releases](https://github.com/Vixxy0w0/qqmusic-rpc-linux/releases)。

## 开源协议

[MIT](LICENSE) — 随意使用和修改。
