# 回响笔记 - 个人博客

这是一个基于 [Pelican](https://getpelican.com/) 静态网站生成器构建的个人博客项目。

## 项目概述

- **博客名称**: 回响笔记
- **作者**: feiyu
- **技术栈**: Python + Pelican + Markdown
- **主题**: gum (自定义主题)

## 项目结构

```
myblog/
├── content/                 # 博客内容目录
│   ├── demo.md             # 示例文章
│   ├── MDW9dXYJ4opI0yxxECZcwhOCnzb.md  # 文章
│   └── static/             # 静态资源
│       ├── CbxYbJcYDo79yWx4cM7ciowpn5f.png
│       └── Ui8MbCtHkoDNbixn2uQcZs7wnxd.png
├── pelican-themes/         # 主题目录
│   └── gum/               # 当前使用的主题
├── output/                 # 生成的静态网站（构建后生成）
├── pelicanconf.py          # 开发环境配置
├── publishconf.py          # 生产环境配置
├── Makefile                # Make命令工具
├── tasks.py                # Invoke任务脚本
└── README.md               # 项目说明
```

## 快速开始

### 环境要求

- Python 3.6+
- Pelican 4.x
- Markdown 支持

### 安装依赖

```bash
pip install pelican markdown
```

### 开发模式

1. **生成网站**
```bash
make html
```

2. **本地预览**
```bash
make serve
```
访问 http://localhost:8000 查看网站

3. **开发服务器（自动重载）**
```bash
make devserver
```

### 使用 Invoke 任务

项目还提供了更强大的 Invoke 任务系统：

```bash
# 清理生成的文件
invoke clean

# 构建网站
invoke build

# 构建并启动本地服务器
invoke reserve

# 实时重载开发服务器
invoke livereload

# 生成生产版本
invoke preview
```

## 写作指南

### 创建新文章

在 `content/` 目录下创建 `.md` 文件，使用以下格式：

```markdown
Title: 文章标题
Date: 2024-01-01 10:00
Category: 分类
Tags: 标签1, 标签2

这里是文章内容...
```

### 文章格式

- 使用 Markdown 语法
- 支持图片、代码块、表格等
- 图片存放在 `content/static/` 目录

## 配置说明

### 主要配置 (pelicanconf.py)

- **AUTHOR**: feiyu
- **SITENAME**: 回响笔记
- **TIMEZONE**: Europe/Rome
- **DEFAULT_LANG**: cn
- **THEME**: pelican-themes/gum
- **STATIC_PATHS**: ['images', 'pdfs', 'files', 'static']

### 生产配置 (publishconf.py)

用于生产环境部署，包含：
- Feed 生成
- 相对URL设置
- 输出目录清理

## 部署

### 生成生产版本

```bash
make publish
```

### 部署到服务器

使用 `invoke publish` 命令（需要配置 SSH 连接信息）：

```bash
invoke publish
```

## 自定义主题

当前使用 `gum` 主题，位于 `pelican-themes/gum/` 目录。

如需修改主题：
1. 编辑主题文件
2. 重新生成网站
3. 重启开发服务器查看效果

使用submodule命令动态引入主题：
`git submodule add https://github.com/Pelican-Elegant/elegant.git themes/elegant`

## 常用命令总结

| 命令 | 功能 |
|------|------|
| `make html` | 生成静态网站 |
| `make serve` | 启动本地服务器 |
| `make devserver` | 开发服务器（自动重载） |
| `make clean` | 清理生成的文件 |
| `make publish` | 生成生产版本 |
| `invoke livereload` | 实时重载开发服务器 |

```
# 生成静态网站（处理 content 目录下的内容）
pelican content

# 启动服务器并绑定到所有网络接口（允许外部设备访问）
pelican --listen -b 0.0.0.0
```