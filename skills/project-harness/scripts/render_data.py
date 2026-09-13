#!/usr/bin/env python3
"""render_data.py — 展示文案数据表（zh/en 双语）。

展示内容与渲染逻辑分离的唯一点：本模块只放"给人看的双语文案表"，
格式化与填充逻辑留在 init_project / scan_repo。修改文案不改逻辑，
修改逻辑不动文案。
"""

from __future__ import annotations

# 配置/环境文件的用途说明（zh, en）——repo-profile「配置文件」表与
# code-index 渲染共用。键为文件基名（清单类）或 scan 的 config kind。
CONFIG_PURPOSE = {
    "package.json": ("Node 清单（name/scripts/依赖）",
                     "Node manifest (name/scripts/deps)"),
    "pyproject.toml": ("Python 工程配置", "Python project configuration"),
    "requirements.txt": ("Python 依赖清单", "Python dependency list"),
    "setup.py": ("Python 打包配置", "Python packaging"),
    "go.mod": ("Go 模块定义", "Go module definition"),
    "pom.xml": ("Maven 工程配置", "Maven project configuration"),
    "build.gradle": ("Gradle 构建配置", "Gradle build configuration"),
    "build.gradle.kts": ("Gradle 构建配置（Kotlin DSL）",
                         "Gradle build configuration (Kotlin DSL)"),
    "CMakeLists.txt": ("CMake 构建配置", "CMake build configuration"),
    "Makefile": ("make 目标定义", "make targets"),
    "Cargo.toml": ("Rust crate 配置", "Rust crate configuration"),
    "nvmrc": ("Node 版本固定", "Node version pin"),
    "python-version": ("Python 版本固定", "Python version pin"),
    "dockerfile": ("容器镜像构建", "container image build"),
    "docker-compose": ("容器编排", "container orchestration"),
    "tox": ("tox 多环境测试", "tox multi-env testing"),
    "gh-workflows": ("GitHub Actions 工作流", "GitHub Actions workflows"),
    "sln": ("Visual Studio 解决方案", "Visual Studio solution"),
    "vcxproj": ("Visual Studio C++ 工程", "Visual Studio C++ project"),
}

# 顶层目录约定说明（zh, en）——top_dirs 探测结果的展示文案。
DIR_CONVENTIONS = {
    "src": ("源码目录", "source code"),
    "tests": ("测试", "tests"), "test": ("测试", "tests"),
    "docs": ("文档", "documentation"), "doc": ("文档", "documentation"),
    "web": ("前端", "frontend"), "frontend": ("前端", "frontend"),
    "client": ("前端/客户端", "frontend/client"),
    "server": ("后端", "backend"), "backend": ("后端", "backend"),
    "api": ("后端 API", "backend API"),
    "cmd": ("命令入口（Go 约定）", "command entrypoints (Go convention)"),
    "scripts": ("脚本", "scripts"), "examples": ("示例", "examples"),
    "internal": ("内部包（Go 约定）", "internal packages (Go convention)"),
    "pkg": ("公共包（Go 约定）", "public packages (Go convention)"),
    "lib": ("库代码", "library code"), "app": ("应用代码", "application code"),
    "config": ("配置", "configuration"), "assets": ("静态资源", "static assets"),
    "public": ("静态资源", "static assets"),
    "docker": ("容器配置", "container config"),
}
