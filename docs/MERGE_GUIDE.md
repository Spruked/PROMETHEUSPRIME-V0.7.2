# Repository Merge Guide

## 🎯 How to Merge Pro Prime Minting Alpha with Another Repository

### Quick Start Commands

1. **Analyze your current setup:**
   ```bash
   python merge_helper.py
   ```

2. **Simple manual merge (recommended for beginners):**
   ```bash
   python merge_helper.py "C:\path\to\target\repo" manual pro-prime-minting
   ```

3. **Advanced git subtree merge:**
   ```bash
   python merge_helper.py "C:\path\to\target\repo" subtree minting-engine
   ```

## 📋 Merge Strategies Explained

### 1. Manual Copy (Easiest)
**Best for:** Simple integration, no git history needed
```bash
# Copy files to target repository
python merge_helper.py "C:\target\repo" manual "my-minting-module"
```

**What it does:**
- Copies all files to target repository
- Creates git commit
- No history preservation
- Easy to understand and modify

### 2. Git Subtree (Advanced)
**Best for:** Preserving history, professional integration
```bash
# Merge with full git history
python merge_helper.py "C:\target\repo" subtree "pro-prime-minting"
```

**What it does:**
- Preserves git history
- Creates proper merge commits
- Allows future updates from source
- Professional approach

### 3. Git Submodule (For linked repos)
**Best for:** Keeping repositories separate but linked
```bash
# After pushing to GitHub/GitLab
cd target-repo
git submodule add https://github.com/your-username/pro-prime-minting.git minting-engine
```

**What it does:**
- Links to external repository
- Keeps repositories separate
- Requires remote repository

## 🔧 Step-by-Step Manual Process

### Option A: Simple File Copy
```bash
# 1. Navigate to your target repository
cd "C:\path\to\target\repo"

# 2. Create subdirectory
mkdir pro-prime-minting

# 3. Copy files
xcopy "C:\Users\bryan\OneDrive\Desktop\Pro_Prime_Minting_Alpha\Alpha mint engine\*" "pro-prime-minting\" /E /H /C /I

# 4. Initialize git if needed
git init

# 5. Add and commit
git add .
git commit -m "Add Pro Prime Minting Alpha module"
```

### Option B: Using the Helper Script
```bash
# 1. Navigate to Pro Prime Minting Alpha directory
cd "C:\Users\bryan\OneDrive\Desktop\Pro_Prime_Minting_Alpha\Alpha mint engine"

# 2. Run the helper
python merge_helper.py "C:\target\repo" manual "minting-engine"
```

## 🏗️ Integration Steps After Merge

### 1. Update Import Paths
If you moved files, update Python imports:
```python
# Before (if files were in root)
from security.input_validator import InputValidator

# After (if moved to subdirectory)
from minting_engine.security.input_validator import InputValidator
```

### 2. Update Configuration Paths
Update any hardcoded paths in configuration files:
```json
{
  "log_path": "./logs/app.log",
  "config_path": "./config/config.json"
}
```

### 3. Merge Dependencies
Combine requirements.txt files:
```bash
# In target repository
cat minting-engine/requirements.txt >> requirements.txt
pip install -r requirements.txt
```

### 4. Update Documentation
- Update README.md in target repo
- Document the new module structure
- Update any deployment scripts

## 🚨 Common Issues and Solutions

### Issue 1: File Path Conflicts
**Problem:** Files with same names in both repositories
**Solution:** 
- Rename conflicting files
- Use subdirectories to organize
- Merge configuration files manually

### Issue 2: Dependency Conflicts
**Problem:** Different versions of same package
**Solution:**
- Use virtual environments
- Update to compatible versions
- Use dependency management tools

### Issue 3: Git History Issues
**Problem:** Complex merge conflicts
**Solution:**
- Use manual merge first
- Clean up history with rebase
- Consider starting fresh repository

## 🎯 Recommended Workflow

### For Simple Integration:
1. **Backup both repositories**
2. **Use manual merge strategy**
3. **Test integration thoroughly**
4. **Update documentation**
5. **Deploy and monitor**

### For Advanced Integration:
1. **Initialize git in source if needed**
2. **Use subtree merge strategy**
3. **Resolve any conflicts**
4. **Update import paths**
5. **Test all functionality**

## 🔍 Pre-Merge Checklist

- [ ] Backup both repositories
- [ ] Check for file name conflicts
- [ ] Review dependency requirements
- [ ] Plan directory structure
- [ ] Test merge strategy on copy first
- [ ] Update documentation plan
- [ ] Prepare rollback plan

## 💡 Best Practices

1. **Always backup before merging**
2. **Test merge on copies first**
3. **Use descriptive commit messages**
4. **Document the merge process**
5. **Update all relevant documentation**
6. **Test thoroughly after merge**

## 🆘 Need Help?

If you encounter issues:
1. Check the error messages carefully
2. Ensure all paths are correct
3. Verify git repository status
4. Try manual merge first
5. Ask for specific error help

## 📞 Support Commands

```bash
# Check current repository status
git status

# See what files would be copied
python merge_helper.py  # (analysis only)

# Undo last commit (if needed)
git reset --soft HEAD~1

# See repository structure
tree /f  # Windows
ls -la   # Linux/Mac
```
