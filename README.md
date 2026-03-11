<div align="center">

# QQ Music Discord RPC (Linux)

[![English](https://img.shields.io/badge/README-English-blue)](#english)
[![简体中文](https://img.shields.io/badge/README-简体中文-red)](#简体中文)

![showcase](https://github.com/user-attachments/assets/73360520-04df-4dcb-b815-8573806b755b)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
![Platform: Linux](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)

</div>

---

<a name="english"></a>
# 🇬🇧 English

> Discord Rich Presence for QQ Music on Linux — shows your current track, artist, album art, and playback state.

## Features

- **Playing & Paused states** — presence updates when you pause, clears only when playback stops entirely
- **Album art** — automatically fetches high-res covers from the QQ Music CDN
- **Smart player detection** — reads from MPRIS (D-Bus), works with the official QQ Music Linux build and Electron wrappers; ignores browsers
- **Isolated install** — uses a Python venv, no sudo, no system package conflicts
- **Auto-start** — runs as a systemd user service that starts on login
- **One-command updates** — `./install.sh --update`

## Requirements

- Linux (any distro with systemd)
- Python 3.8+
- `python3-venv` (see below if missing)
- Discord desktop app (not browser)
- QQ Music (official Linux build or an Electron wrapper)

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
- Make sure a song is actually playing
- Check logs: `journalctl --user -u qqmusic-rpc -f`

**Art not loading**
- Normal for obscure tracks — falls back to the QQ Music logo
- Check your internet connection if happening for all tracks

**Service crashes on startup**
- Run `journalctl --user -u qqmusic-rpc -n 30 --no-pager` and check the error
- Make sure Discord is open before or shortly after the service starts

**Works manually but not as a service**
- Make sure `~/.local/bin` is in your `$PATH`. Add this to `~/.bashrc` or `~/.zshrc`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

## How it works

The script polls the session D-Bus every 5 seconds using the [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) interface (`org.mpris.MediaPlayer2`), which QQ Music exposes automatically. It filters out browsers and non-music players, reads track metadata, fetches album art from the QQ Music CDN, and updates Discord via `pypresence`.

## Changelog

See [Releases](https://github.com/Vixxy0w0/qqmusic-rpc-linux/releases) for version history.

## License

[MIT](LICENSE)

---

<a name="简体中文"></a>
# 🇨🇳 简体中文

> 在 Linux 上为 QQ 音乐实现 Discord 状态同步，显示当前播放的歌曲、歌手、专辑封面及播放状态。

## 功能特点

- **播放与暂停状态同步** — 暂停时状态更新为暂停，仅在完全停止播放时才清除状态
- **自动获取专辑封面** — 从 QQ 音乐 CDN 自动拉取高清封面
- **智能识别播放器** — 通过 MPRIS（D-Bus）读取播放信息，支持官方 Linux 版及第三方 Electron 封装版；自动屏蔽浏览器
- **纯净安装** — 使用 Python 虚拟环境，无需 sudo，不污染系统包
- **开机自启** — 以 systemd 用户服务运行，登录后自动启动
- **一键更新** — `./install.sh --update`

## 运行要求

- Linux（任意带有 systemd 的发行版）
- Python 3.8 及以上
- `python3-venv`（缺失时见下方说明）
- Discord 桌面客户端（不支持网页版）
- QQ 音乐（官方 Linux 版或第三方 Electron 封装版）

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
- 冷门歌曲可能无法获取封面，会自动回退显示 QQ 音乐图标
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

脚本每 5 秒通过 [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) 接口（`org.mpris.MediaPlayer2`）轮询 D-Bus 会话总线——这是 QQ 音乐自动暴露的标准接口。脚本会过滤掉浏览器和非音乐播放器，读取歌曲元数据，从 QQ 音乐 CDN 获取专辑封面，并通过 `pypresence` 更新 Discord 状态。

## 更新日志

版本历史请查看 [Releases](https://github.com/Vixxy0w0/qqmusic-rpc-linux/releases)。

## 开源协议

[MIT](LICENSE) — 随意使用和修改。
