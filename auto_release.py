#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布助手：将 dist 目录中的 EXE 文件发布到 GitHub/Gitee/GitCode Releases

功能：
1. 检测 dist 目录中的最新版本 EXE
2. 自动创建 Git Tag
3. 推送 Tag 到所有远程仓库
4. 生成 Release 描述模板
5. 提供各平台发布链接

使用方法：
    python auto_release.py
    
或者指定版本号：
    python auto_release.py v260521-A2
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime


class AutoReleaseHelper:
    """自动发布助手"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.remote_repos = {
            'origin': None,  # GitHub
            'gitee': None,   # Gitee
            'gitcode': None  # GitCode
        }
        
    def get_latest_exe(self):
        """获取最新的版本化 EXE 文件"""
        if not self.dist_dir.exists():
            print("❌ dist 目录不存在，请先运行打包脚本")
            return None
            
        # 查找 QML_*.exe 文件
        exe_files = list(self.dist_dir.glob("QML_*.exe"))
        
        if not exe_files:
            print("❌ 未找到版本化的 EXE 文件（QML_*.exe）")
            print("💡 提示：请先运行 python build_exe.py 进行打包")
            return None
        
        # 按文件名排序，取最新的
        exe_files.sort(reverse=True)
        latest_exe = exe_files[0]
        
        return latest_exe
    
    def extract_version_from_filename(self, filename):
        """从文件名提取版本号"""
        # QML_260521_A2.exe -> v260521-A2
        match = re.search(r'QML_(\d{6})_([A-Z0-9]{2})', filename)
        if match:
            date_part = match.group(1)
            time_part = match.group(2)
            return f"v{date_part}-{time_part}"
        return None
    
    def check_git_status(self):
        """检查 Git 状态"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                print("⚠️  检测到未提交的更改：")
                print(result.stdout)
                response = input("是否继续？(y/n): ")
                if response.lower() != 'y':
                    return False
            
            return True
        except Exception as e:
            print(f"❌ 检查 Git 状态失败: {e}")
            return False
    
    def get_remote_urls(self):
        """获取远程仓库 URL"""
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 2:
                    remote_name = parts[0]
                    url = parts[1]
                    
                    if remote_name in self.remote_repos:
                        self.remote_repos[remote_name] = url
            
            return True
        except Exception as e:
            print(f"❌ 获取远程仓库信息失败: {e}")
            return False
    
    def create_git_tag(self, version):
        """创建 Git Tag"""
        try:
            # 检查 tag 是否已存在
            result = subprocess.run(
                ['git', 'tag', '-l', version],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                print(f"⚠️  Tag {version} 已存在")
                response = input("是否删除并重新创建？(y/n): ")
                if response.lower() == 'y':
                    subprocess.run(
                        ['git', 'tag', '-d', version],
                        cwd=self.project_root
                    )
                else:
                    return False
            
            # 创建新 tag
            print(f"🏷️  创建 Git Tag: {version}")
            result = subprocess.run(
                ['git', 'tag', '-a', version, '-m', f'Release {version}'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ Tag {version} 创建成功")
                return True
            else:
                print(f"❌ 创建 Tag 失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 创建 Tag 异常: {e}")
            return False
    
    def push_tags(self):
        """推送 Tags 到所有远程仓库"""
        print("\n📤 推送 Tags 到远程仓库...")
        
        success_count = 0
        total_count = 0
        
        for remote_name, url in self.remote_repos.items():
            if not url:
                print(f"⚠️  {remote_name}: 未配置")
                continue
            
            total_count += 1
            print(f"  → 推送到 {remote_name}...", end=' ')
            
            try:
                result = subprocess.run(
                    ['git', 'push', remote_name, '--tags'],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅")
                    success_count += 1
                else:
                    print(f"❌ {result.stderr[:50]}")
                    
            except subprocess.TimeoutExpired:
                print("⏱️  超时")
            except Exception as e:
                print(f"❌ {str(e)[:50]}")
        
        print(f"\n📊 推送结果: {success_count}/{total_count} 成功")
        return success_count > 0
    
    def generate_release_notes(self, version, exe_file):
        """生成 Release 说明"""
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日 %H:%M")
        
        notes = f"""## 🎉 {version.replace('v', 'QML_').replace('-', '_')} 发布

**构建时间**: {date_str}  
**版本号**: {version.replace('v', '')}

### ✨ 更新内容
- （请在此处添加新功能说明）

### 🐛 Bug 修复
- （请在此处添加修复的问题）

### 📦 下载
- [{exe_file.name}](附件) - 主程序（推荐）

### 📋 系统要求
- Windows 操作系统
- LoongArch 架构支持
- QEMU for LoongArch

### 🔗 相关链接
- [项目主页](仓库URL)
- [完整文档](docs/INDEX.md)
- [命名规则](docs/EXE_NAMING_RULES.md)
- [发布指南](docs/RELEASE_GUIDE.md)
"""
        return notes
    
    def print_release_links(self, version):
        """打印各平台的 Release 创建链接"""
        print("\n" + "="*60)
        print("📋 请在以下平台创建 Release")
        print("="*60)
        
        platforms = {
            'GitHub': 'https://github.com/{user}/{repo}/releases/new',
            'Gitee': 'https://gitee.com/{user}/{repo}/releases/new',
            'GitCode': 'https://gitcode.com/{user}/{repo}/releases/new'
        }
        
        for platform, template in platforms.items():
            remote_name = platform.lower()
            if remote_name == 'github':
                remote_name = 'origin'
            
            url = self.remote_repos.get(remote_name)
            if url:
                # 提取 user/repo
                match = re.search(r'[:/]([^/]+)/([^.]+)\.git', url)
                if match:
                    user = match.group(1)
                    repo = match.group(2)
                    release_url = template.format(user=user, repo=repo)
                    print(f"\n{platform}:")
                    print(f"  🔗 {release_url}")
                    print(f"  📝 Tag: {version}")
                    print(f"  📎 上传文件: {self.latest_exe.name}")
                else:
                    print(f"\n{platform}: 无法解析 URL")
            else:
                print(f"\n{platform}: 未配置")
        
        print("\n" + "="*60)
    
    def save_release_notes(self, version, notes):
        """保存 Release 说明到文件"""
        notes_file = self.project_root / f"RELEASE_NOTES_{version}.md"
        
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        print(f"\n💾 Release 说明已保存到: {notes_file}")
        print(f"📄 可以复制以下内容到各平台：")
        print("-"*60)
        print(notes)
        print("-"*60)
    
    def run(self, custom_version=None):
        """执行发布流程"""
        print("="*60)
        print("🚀 Deepin VM Manager - 自动发布助手")
        print("="*60)
        print()
        
        # 1. 获取最新 EXE
        print("📦 步骤 1: 查找最新的 EXE 文件")
        self.latest_exe = self.get_latest_exe()
        if not self.latest_exe:
            return False
        
        print(f"✅ 找到: {self.latest_exe.name}")
        print(f"📍 路径: {self.latest_exe}")
        print()
        
        # 2. 确定版本号
        if custom_version:
            version = custom_version
        else:
            version = self.extract_version_from_filename(self.latest_exe.name)
        
        if not version:
            print("❌ 无法从文件名提取版本号")
            version = input("请手动输入版本号（格式：vYYMMDD-HM）: ")
        
        print(f"🏷️  版本号: {version}")
        print()
        
        # 3. 检查 Git 状态
        print("📋 步骤 2: 检查 Git 状态")
        if not self.check_git_status():
            return False
        print()
        
        # 4. 获取远程仓库
        print("🌐 步骤 3: 获取远程仓库信息")
        if not self.get_remote_urls():
            return False
        
        configured_remotes = [name for name, url in self.remote_repos.items() if url]
        if not configured_remotes:
            print("❌ 未配置任何远程仓库")
            print("💡 提示：先添加远程仓库")
            print("   git remote add origin <GitHub URL>")
            print("   git remote add gitee <Gitee URL>")
            print("   git remote add gitcode <GitCode URL>")
            return False
        
        print(f"✅ 已配置的远程仓库: {', '.join(configured_remotes)}")
        print()
        
        # 5. 创建 Git Tag
        print("🏷️  步骤 4: 创建 Git Tag")
        if not self.create_git_tag(version):
            return False
        print()
        
        # 6. 推送 Tags
        print("📤 步骤 5: 推送 Tags")
        if not self.push_tags():
            print("⚠️  Tag 推送失败，但可以继续手动创建 Release")
        print()
        
        # 7. 生成 Release 说明
        print("📝 步骤 6: 生成 Release 说明")
        notes = self.generate_release_notes(version, self.latest_exe)
        self.save_release_notes(version, notes)
        print()
        
        # 8. 打印发布链接
        self.print_release_links(version)
        
        print("\n" + "="*60)
        print("✅ 自动发布准备完成！")
        print("="*60)
        print("\n📌 下一步操作：")
        print("1. 点击上面的链接访问各平台")
        print("2. 选择 Tag: " + version)
        print("3. 粘贴 Release 说明")
        print("4. 上传文件: " + self.latest_exe.name)
        print("5. 点击发布")
        print()
        
        return True


def main():
    """主函数"""
    helper = AutoReleaseHelper()
    
    # 检查命令行参数
    custom_version = None
    if len(sys.argv) > 1:
        custom_version = sys.argv[1]
        if not custom_version.startswith('v'):
            custom_version = 'v' + custom_version
    
    success = helper.run(custom_version)
    
    if success:
        print("\n🎉 完成！请访问各平台创建 Release")
    else:
        print("\n❌ 发布准备失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
