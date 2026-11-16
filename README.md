# 我的 Linux 开发配置

2026-11-16 从 Ubuntu 22.04 实机配置整理，用于迁到 Red Hat 8。保留编辑器、终端、字体、输入法等个人配置；软件和插件按版本清单在新机核对或安装。

## 恢复

```bash
git clone https://github.com/roundeodo/dotfiles.git ~/dotfiles
cd ~/dotfiles
python3 install.py
python3 install.py --apply
```

第一条安装命令只预览。`--apply` 才会写入，覆盖前把原文件保存到 `~/.local/state/dotfiles/backups/`。脚本保留新机 `.bashrc` 的原内容，包括 Red Hat 的 `/etc/bashrc` 初始化，只追加个人设置。配置中的 `/home/yong` 会替换为当前用户 home。

- `home/`：按用户目录结构保存的配置，包括 VS Code 设置/快捷键、Vim、Coc、Git、tmux、输入法、字体和自定义 SystemVerilog 格式化脚本。
- `reference/`：软件版本、VS Code 扩展 ID@版本、Vim 插件提交、筛选过的 GNOME 设置。
- `reference/ubuntu-home/`：原 Bash/profile/输入法启动设置，只作参考，不覆盖 Red Hat 初始化文件。
- 根目录 `bashrc`、`vimrc` 保留常见 dotfiles 文件入口，其中 `bashrc` 是原 Ubuntu 配置参考；恢复应使用安装脚本。

## 补齐编辑器依赖

字体恢复后运行 `fc-cache -f`。Vim 插件恢复到记录的提交：

```bash
python3 sync_vim_plugins.py
python3 sync_vim_plugins.py --apply
```

VS Code 扩展及版本见 `reference/vscode-extensions.txt`。如新机缺失相应扩展且该版本支持新机，可安装：

```bash
while IFS= read -r extension; do
    [ -z "$extension" ] || code --install-extension "$extension"
done < reference/vscode-extensions.txt
```

格式化、补全和构建还依赖 Verible、slang-server、clang-format、Node、RISC-V 编译器等。原路径与部分版本保存在 `reference/tool-paths-and-versions.txt`；按新机实际安装位置修改相应配置。旧机的 Vim.AppImage 和 oss-cad-suite 路径没有加入新 Bash 初始化。

`reference/desktop-settings.dconf` 保存筛选后的桌面、终端、输入法、键盘等设置，仅对新机 GNOME 支持的项逐项恢复；不直接覆盖 Ubuntu 的 dconf 数据库或 `/etc`。两种发行版的软件版本可能不同，最终要实际检查字体、快捷键、补全和格式化。

## 未公开上传的内容

SSH/GPG 私钥、令牌、Cookie、登录数据库、编辑器聊天历史、在线账号配置、输入法学习历史和系统标识均不上传。新机生成 SSH 密钥后在 GitHub 重新授权，编辑器等服务重新登录。具体排除路径见 `reference/excluded-private-paths.json`。

项目当前源码与本地历史另存于 [ysyx 的迁移分支](https://github.com/roundeodo/ysyx/tree/migration-2026-11-16)。
