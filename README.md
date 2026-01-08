# QQ Music Discord RPC (Linux) | QQ音乐 Discord 同步

**A lightweight, zero-config Rich Presence for QQ Music on Linux.**
**专为 Linux 用户打造的 QQ 音乐 Discord RPC 插件。零配置，装完即用。**

<img width="327" height="138" alt="Showcase" src="https://github.com/user-attachments/assets/73360520-04df-4dcb-b815-8573806b755b" />



## Features | 功能特点

* **Smart Detection**: Works with official QQ Music & Electron wrappers.
    * **自动识别**：支持官方 Linux 版及第三方版本。
* **Album Art**: Fetches high-res covers automatically.
    * **封面同步**：自动抓取高清专辑封面。
* **Zero Config**: Installs to `~/.local/share`.
    * **纯净安装**：无需 Sudo 权限，不污染系统。

---

## Installation | 食用方法

### 1. Download | 下载
```bash
git clone [https://github.com/Vixxy0w0/qqmusic-rpc-linux.git](https://github.com/Vixxy0w0/qqmusic-rpc-linux.git)
cd qqmusic-rpc-linux

```

### 2. Installation | 一键安装

```bash
chmod +x install.sh
./install.sh

```

**The service is now running in the background.**
**搞定！服务已经在后台运行了，下次开机会自动启动。**

---

## Controls | 常用命令

### Restart Service (重启服务):

```bash
systemctl --user restart qqmusic-rpc

```

### Stop Service (停止服务):

```bash
systemctl --user stop qqmusic-rpc

```

### View Logs (查看日志/报错):

```bash
journalctl --user -u qqmusic-rpc -f

```

---

## Uninstall | 卸载

If you want to remove the service completely:

如果你想彻底删除本插件：

### 1. Stop and disable the service | 停止并禁用服务

```bash
systemctl --user stop qqmusic-rpc
systemctl --user disable qqmusic-rpc

```

### 2. Remove files and shortcuts | 删除文件和快捷方式
```bash
rm ~/.config/systemd/user/qqmusic-rpc.service
rm ~/.local/bin/qqmusic-rpc
rm -rf ~/.local/share/qqmusic-rpc

```

### 3. Reload system settings | 刷新系统设置

```bash
systemctl --user daemon-reload

```

---

## FAQ | 常见问题

### Q: It's not showing up on Discord? (Discord 没显示状态？)

* **A:** Check if "Activity Privacy" -> "Share your detected activities" is ON in Discord settings. Also, play a song! It won't show anything if paused.

### Q: "pip3 not found"?

* **A:** You need to install pip.
* **Ubuntu/Debian:** `sudo apt install python3-pip`
* **Arch/Manjaro:** `sudo pacman -S python-pip`
* **Fedora:** `sudo dnf install python3-pip`
