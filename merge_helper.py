#!/usr/bin/env python3
"""
Repository Merge Helper for Pro Prime Minting Alpha
Helps merge this module with another repository using various strategies.
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile

class RepositoryMerger:
    """Helper class for merging repositories."""
    
    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.merge_strategies = {
            'subtree': self._merge_subtree,
            'submodule': self._merge_submodule,
            'manual': self._merge_manual,
            'filter-branch': self._merge_filter_branch
        }
        
    def analyze_source(self) -> Dict[str, Any]:
        """Analyze the source repository/folder."""
        print("🔍 Analyzing source repository...")
        
        analysis = {
            'path': str(self.source_path),
            'is_git_repo': self._is_git_repo(self.source_path),
            'size': self._get_folder_size(self.source_path),
            'file_count': self._count_files(self.source_path),
            'structure': self._get_folder_structure(self.source_path),
            'dependencies': self._analyze_dependencies(),
            'config_files': self._find_config_files(),
            'recommendations': []
        }
        
        # Add recommendations based on analysis
        if analysis['is_git_repo']:
            analysis['recommendations'].append("Source has git history - consider subtree merge")
        else:
            analysis['recommendations'].append("No git history - manual copy or init git first")
            
        if analysis['file_count'] > 100:
            analysis['recommendations'].append("Large project - consider submodule approach")
            
        return analysis
        
    def prepare_for_merge(self, target_path: str, strategy: str = 'subtree') -> Dict[str, Any]:
        """Prepare source for merging with target repository."""
        print(f"🔧 Preparing for {strategy} merge...")
        
        target_path = Path(target_path)
        
        # Create preparation plan
        plan = {
            'strategy': strategy,
            'source_path': str(self.source_path),
            'target_path': str(target_path),
            'steps': [],
            'conflicts': [],
            'backup_needed': True
        }
        
        # Check target repository
        if not target_path.exists():
            plan['steps'].append(f"Create target directory: {target_path}")
            plan['conflicts'].append("Target directory does not exist")
            
        if not self._is_git_repo(target_path):
            plan['steps'].append("Initialize git repository in target")
            
        # Strategy-specific preparation
        if strategy == 'subtree':
            plan['steps'].extend(self._prepare_subtree_merge(target_path))
        elif strategy == 'submodule':
            plan['steps'].extend(self._prepare_submodule_merge(target_path))
        elif strategy == 'manual':
            plan['steps'].extend(self._prepare_manual_merge(target_path))
        elif strategy == 'filter-branch':
            plan['steps'].extend(self._prepare_filter_branch_merge(target_path))
            
        return plan
        
    def execute_merge(self, target_path: str, strategy: str = 'subtree', 
                     subfolder: str = None) -> bool:
        """Execute the merge operation."""
        print(f"🚀 Executing {strategy} merge...")
        
        try:
            if strategy in self.merge_strategies:
                return self.merge_strategies[strategy](target_path, subfolder)
            else:
                print(f"❌ Unknown strategy: {strategy}")
                return False
                
        except Exception as e:
            print(f"❌ Merge failed: {str(e)}")
            return False
            
    def _is_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        return (path / '.git').exists()
        
    def _get_folder_size(self, path: Path) -> int:
        """Get folder size in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = Path(dirpath) / f
                try:
                    total_size += fp.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
        return total_size
        
    def _count_files(self, path: Path) -> int:
        """Count total files in directory."""
        count = 0
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count
        
    def _get_folder_structure(self, path: Path, max_depth: int = 3) -> List[str]:
        """Get folder structure up to max_depth."""
        structure = []
        
        def _add_items(current_path: Path, current_depth: int, prefix: str = ""):
            if current_depth > max_depth:
                return
                
            try:
                items = sorted(current_path.iterdir())
                for item in items:
                    if item.is_dir():
                        structure.append(f"{prefix}📁 {item.name}/")
                        _add_items(item, current_depth + 1, prefix + "  ")
                    else:
                        structure.append(f"{prefix}📄 {item.name}")
            except PermissionError:
                structure.append(f"{prefix}❌ Permission denied")
                
        _add_items(path, 0)
        return structure[:50]  # Limit to 50 items
        
    def _analyze_dependencies(self) -> List[str]:
        """Analyze project dependencies."""
        dependencies = []
        
        # Check for Python requirements
        req_file = self.source_path / 'requirements.txt'
        if req_file.exists():
            dependencies.append("Python requirements.txt found")
            
        # Check for package.json
        package_file = self.source_path / 'package.json'
        if package_file.exists():
            dependencies.append("Node.js package.json found")
            
        # Check for other dependency files
        dep_files = ['Pipfile', 'poetry.lock', 'yarn.lock', 'composer.json']
        for dep_file in dep_files:
            if (self.source_path / dep_file).exists():
                dependencies.append(f"{dep_file} found")
                
        return dependencies
        
    def _find_config_files(self) -> List[str]:
        """Find configuration files that might cause conflicts."""
        config_files = []
        
        # Common config files
        common_configs = [
            '.env', '.env.example', 'config.json', 'config.yaml',
            '.gitignore', 'README.md', 'LICENSE', 'Dockerfile'
        ]
        
        for config in common_configs:
            if (self.source_path / config).exists():
                config_files.append(config)
                
        # Find config directories
        config_dirs = ['config', 'configs', 'settings', '.vscode']
        for config_dir in config_dirs:
            if (self.source_path / config_dir).exists():
                config_files.append(f"{config_dir}/")
                
        return config_files
        
    def _prepare_subtree_merge(self, target_path: Path) -> List[str]:
        """Prepare for subtree merge."""
        steps = []
        
        # Initialize git in source if not already
        if not self._is_git_repo(self.source_path):
            steps.append("Initialize git repository in source")
            steps.append("Add and commit all files in source")
            
        steps.append("Add source as remote in target repository")
        steps.append("Execute git subtree merge")
        
        return steps
        
    def _prepare_submodule_merge(self, target_path: Path) -> List[str]:
        """Prepare for submodule merge."""
        steps = []
        
        steps.append("Source needs to be in a separate git repository")
        steps.append("Push source repository to remote (GitHub/GitLab)")
        steps.append("Add as submodule in target repository")
        
        return steps
        
    def _prepare_manual_merge(self, target_path: Path) -> List[str]:
        """Prepare for manual merge."""
        steps = []
        
        steps.append("Copy files from source to target")
        steps.append("Resolve any file conflicts")
        steps.append("Update configuration files")
        steps.append("Commit changes in target repository")
        
        return steps
        
    def _prepare_filter_branch_merge(self, target_path: Path) -> List[str]:
        """Prepare for filter-branch merge."""
        steps = []
        
        steps.append("Create temporary repository copy")
        steps.append("Use git filter-branch to rewrite history")
        steps.append("Merge rewritten history into target")
        
        return steps
        
    def _merge_subtree(self, target_path: str, subfolder: str = None) -> bool:
        """Execute subtree merge."""
        print("🌳 Executing subtree merge...")
        
        target_path = Path(target_path)
        subfolder = subfolder or "pro-prime-minting"
        
        try:
            # Initialize git in source if needed
            if not self._is_git_repo(self.source_path):
                print("Initializing git in source...")
                subprocess.run(['git', 'init'], cwd=self.source_path, check=True)  # nosec: B603,B607
                subprocess.run(['git', 'add', '.'], cwd=self.source_path, check=True)  # nosec: B603,B607
                subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.source_path, check=True)  # nosec: B603,B607
                
            # Initialize git in target if needed
            if not self._is_git_repo(target_path):
                print("Initializing git in target...")
                target_path.mkdir(parents=True, exist_ok=True)
                subprocess.run(['git', 'init'], cwd=target_path, check=True)  # nosec: B603,B607
                
            # Add source as remote
            print("Adding source as remote...")
            remote_name = "pro-prime-source"
            subprocess.run(['git', 'remote', 'add', remote_name, str(self.source_path)], 
                             cwd=target_path, check=True)  # nosec: B603,B607
            
            # Fetch from source
            print("Fetching from source...")
            subprocess.run(['git', 'fetch', remote_name], cwd=target_path, check=True)  # nosec: B603,B607
            
            # Add subtree
            print(f"Adding subtree to {subfolder}...")
            subprocess.run(['git', 'subtree', 'add', '--prefix', subfolder, 
                           remote_name, 'master', '--squash'], cwd=target_path, check=True)  # nosec: B603,B607
            
            print("✅ Subtree merge completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git command failed: {e}")
            return False
            
    def _merge_submodule(self, target_path: str, subfolder: str = None) -> bool:
        """Execute submodule merge."""
        print("📦 Executing submodule merge...")
        
        print("❌ Submodule merge requires a remote repository URL.")
        print("Please push your source to GitHub/GitLab first, then use:")
        print("git submodule add <repository-url> <path>")
        
        return False
        
    def _merge_manual(self, target_path: str, subfolder: str = None) -> bool:
        """Execute manual merge."""
        print("📋 Executing manual merge...")
        
        target_path = Path(target_path)
        subfolder = subfolder or "pro-prime-minting"
        destination = target_path / subfolder
        
        try:
            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            print(f"Copying files to {destination}...")
            if destination.exists():
                shutil.rmtree(destination)
                
            shutil.copytree(self.source_path, destination)
            
            # Initialize git if needed
            if not self._is_git_repo(target_path):
                print("Initializing git repository...")
                subprocess.run(['git', 'init'], cwd=target_path, check=True)  # nosec: B603,B607
                
            # Add and commit
            print("Adding and committing files...")
            subprocess.run(['git', 'add', '.'], cwd=target_path, check=True)  # nosec: B603,B607
            subprocess.run(['git', 'commit', '-m', 'Add Pro Prime Minting Alpha module'], 
                           cwd=target_path, check=True)  # nosec: B603,B607
            
            print("✅ Manual merge completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Manual merge failed: {e}")
            return False
            
    def _merge_filter_branch(self, target_path: str, subfolder: str = None) -> bool:
        """Execute filter-branch merge."""
        print("🔄 Filter-branch merge is complex and not recommended for most cases.")
        print("Consider using subtree or manual merge instead.")
        
        return False

def main():
    """Main function for interactive repository merging."""
    print("🔄 Pro Prime Minting Alpha - Repository Merger")
    print("=" * 50)
    
    # Get current directory as source
    source_path = os.getcwd()
    print(f"Source: {source_path}")
    
    # Initialize merger
    merger = RepositoryMerger(source_path)
    
    # Analyze source
    analysis = merger.analyze_source()
    
    print(f"\n📊 Source Analysis:")
    print(f"   Files: {analysis['file_count']}")
    print(f"   Size: {analysis['size'] / (1024*1024):.1f} MB")
    print(f"   Git repo: {analysis['is_git_repo']}")
    
    print(f"\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   • {rec}")
    
    # Interactive mode
    if len(sys.argv) < 2:
        print(f"\n🎯 Usage Examples:")
        print(f"   python merge_helper.py <target_path> [strategy] [subfolder]")
        print(f"   python merge_helper.py C:/target/repo subtree pro-prime")
        print(f"   python merge_helper.py C:/target/repo manual minting-engine")
        print(f"\n📝 Strategies: subtree, submodule, manual, filter-branch")
        return
        
    # Get parameters
    target_path = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'subtree'
    subfolder = sys.argv[3] if len(sys.argv) > 3 else 'pro-prime-minting'
    
    # Prepare merge
    plan = merger.prepare_for_merge(target_path, strategy)
    
    print(f"\n📋 Merge Plan ({strategy}):")
    for step in plan['steps']:
        print(f"   • {step}")
        
    if plan['conflicts']:
        print(f"\n⚠️  Potential Conflicts:")
        for conflict in plan['conflicts']:
            print(f"   • {conflict}")
            
    # Confirm and execute
    response = input(f"\n❓ Execute {strategy} merge? (y/N): ")
    if response.lower() == 'y':
        success = merger.execute_merge(target_path, strategy, subfolder)
        if success:
            print(f"\n🎉 Merge completed successfully!")
            print(f"   Target: {target_path}")
            print(f"   Subfolder: {subfolder}")
        else:
            print(f"\n❌ Merge failed. Check errors above.")
    else:
        print("Merge cancelled.")

if __name__ == "__main__":
    main()
