# 🚀 Deploy to Streamlit Cloud via GitHub - Step by Step

Your model files total **~1.3 GB**, so you'll need Git LFS (Large File Storage).

## 📦 Your Large Files:
- `fake_news_model.joblib` - 1222.57 MB ⚠️
- `resnet50_best_fixed.keras` - 89.19 MB
- `tokenizer.joblib` - 2.83 MB

---

## Step 1: Install Git LFS

**Download and install Git LFS:**
- Download from: https://git-lfs.github.com/
- Or use Chocolatey: `choco install git-lfs`
- Or use winget: `winget install GitHub.GitLFS`

After installation, run:
```powershell
git lfs install
```

---

## Step 2: Initialize Git Repository

```powershell
# Navigate to your project folder (if not already there)
cd "d:\PGCHRIST\MMS META\fake news\a"

# Initialize git repository
git init

# Configure Git LFS to track large files (already configured in .gitattributes)
git lfs track "*.joblib"
git lfs track "*.keras"

# Verify LFS is tracking the right files
git lfs track
```

---

## Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., "fake-news-detector")
3. Choose **Public** (required for free Streamlit Cloud)
4. **DO NOT** initialize with README, .gitignore, or license (you already have these)
5. Click "Create repository"

---

## Step 4: Add Files and Push to GitHub

```powershell
# Add all files
git add .

# Commit (first commit may take time due to large files)
git commit -m "Initial commit with ML models"

# Add GitHub remote (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main
git branch -M main

# Push to GitHub (this will upload large files via LFS)
git push -u origin main
```

**⏱️ Note:** Uploading 1.2 GB may take 10-30 minutes depending on your internet speed.

---

## Step 5: Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Fill in the details:**
   - Repository: `YOUR_USERNAME/YOUR_REPO_NAME`
   - Branch: `main`
   - Main file path: `app.py`

5. **Advanced settings (click dropdown):**
   - Python version: `3.11`
   - (Leave other settings as default)

6. **Click "Deploy"**

7. **Wait for deployment** (5-10 minutes for first deployment)

---

## ⚠️ Important Notes

### Git LFS Bandwidth Limits (Free Tier):
- **Storage:** 1 GB (your files are ~1.3 GB)
- **Bandwidth:** 1 GB/month

**You're slightly over the free storage limit!** Options:

**Option A: GitHub LFS Free Tier Workaround**
- Your storage is 1.3 GB (slightly over)
- GitHub may still allow this, or you can buy LFS data packs
- $5/month for 50 GB storage + 50 GB bandwidth

**Option B: Use External Storage (Recommended for >1GB)**
- Store large models in cloud storage (AWS S3, Google Drive, Dropbox)
- Download them when the app starts
- This keeps your repo light

**Option C: Optimize Models**
- Compress models or use quantization
- Remove unused models if you have multiple versions

---

## 🐛 Troubleshooting

**"This exceeds GitHub's file size limit of 100 MB"**
- Make sure Git LFS is installed: `git lfs install`
- Check LFS is tracking: `git lfs track`
- Ensure `.gitattributes` exists

**"LFS bandwidth exceeded"**
- Wait until next month, or
- Upgrade to paid LFS, or
- Use external storage

**Streamlit Cloud deployment fails:**
- Check app logs in Streamlit Cloud dashboard
- Verify all model files uploaded correctly
- Ensure requirements.txt has all dependencies

---

## 🎯 Quick Commands Reference

```powershell
# Check LFS status
git lfs ls-files

# Check repository size
git count-objects -vH

# Force push (if needed)
git push -f origin main

# Check LFS bandwidth usage
git lfs status
```

---

## 📊 Alternative: Download Models on Startup

If you exceed GitHub limits, modify your app to download models from cloud storage:

```python
import os
import requests

def download_model(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)

# In your load_model functions:
download_model('YOUR_S3_URL/fake_news_model.joblib', 'fake_news_model.joblib')
```

Let me know if you need help setting up cloud storage!

---

Good luck with your deployment! 🎉
