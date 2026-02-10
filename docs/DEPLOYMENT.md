# AI Detection Suite - Deployment Guide

This application is a Streamlit-based AI Detection Suite that includes website credibility analysis, AI image detection, and fake news detection (powered by Gemini AI).

## 📋 Prerequisites

Before deploying, ensure you have:
- Model files for website credibility (`.joblib` files) and image detection (`.keras` file)
- **Gemini API Key** for fake news detection (free at https://makersuite.google.com/app/apikey)
- Python 3.11 (specified in runtime.txt)
- Git installed and configured

## 🎯 Key Updates (v2.0)

**Fake News Detection Now Uses Gemini API:**
- ✅ No more 1.2GB model download
- ✅ Faster and more accurate analysis
- ✅ Easier deployment (no large files)
- ✅ Real-time AI-powered fact-checking
- 🔑 Requires free Gemini API key (get at https://makersuite.google.com/app/apikey)

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

**Steps:**

1. **Push to GitHub**
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Deploy AI Detection Suite with Gemini integration"
   
   # Create a new repository on GitHub and then:
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch (main), and main file (app.py)
   - Click "Deploy"

3. **Configure API Key (Important!)**
   - Users will need to enter their Gemini API key in the app sidebar
   - Alternatively, set as Streamlit Secret for automatic use:
     - In Streamlit Cloud dashboard, go to your app
     - Click "Settings" → "Secrets"
     - Add: `GEMINI_API_KEY = "your-api-key-here"`

**Important Notes:**
- Free tier includes 1 GB of storage and resources
- Website and image models are small enough for free tier
- No large fake news model needed anymore (uses API instead)
- Python 3.11 specified in runtime.txt for compatibility

---

### Option 2: Docker Deployment (AWS, GCP, Azure, DigitalOcean)

**Create a Dockerfile:**
Create a file named `Dockerfile` in your project root with the provided configuration.

**Deploy to Cloud Platforms:**

**AWS (Elastic Beanstalk or ECS):**
```bash
# Install AWS CLI and EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p docker your-app-name
eb create your-environment-name
eb open
```

**Google Cloud Run:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fake-news-app
gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/fake-news-app --platform managed
```

**Azure Container Instances:**
```bash
# Build and push to Azure Container Registry
az acr build --registry YOUR_REGISTRY --image fake-news-app .
az container create --resource-group YOUR_RG --name fake-news-app \
  --image YOUR_REGISTRY.azurecr.io/fake-news-app --cpu 2 --memory 4
```

---

### Option 3: Heroku (Simple PaaS)

**Note:** Heroku ended free tier, but paid plans start at $5/month.

1. **Create Heroku account** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI:**
   ```bash
   # Windows (using chocolatey)
   choco install heroku-cli
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

---

### Option 4: Local/VPS Server Deployment

**On Ubuntu/Debian server:**

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Clone your repository
git clone YOUR_REPO_URL
cd YOUR_REPO_NAME

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run with systemd (production) or screen (development)
# Development:
streamlit run app.py --server.port 8501

# Production (create systemd service)
# See DEPLOYMENT_SETUP.md for systemd configuration
```

---

## 🔧 Configuration

### Environment Variables (if needed)
Create `.streamlit/secrets.toml` for sensitive data:
```toml
# API keys or secrets (if your app uses any)
# api_key = "your-api-key"
```

### Memory Considerations
Your app loads multiple ML models. Ensure your deployment platform has:
- Minimum 2 GB RAM
- Recommended 4 GB RAM for smooth operation

---

## 📊 Model Files Required

Ensure these files are in your repository:
- `stacking_model.joblib` (Website credibility)
- `feature_names.joblib`
- `model_metadata.json`
- `resnet50_best_FIXED.keras` (AI image detection)
- `config.joblib` (Fake news)
- `tokenizer.joblib` (Fake news)
- Any CSV files for trusted/untrusted sources

---

## 🧪 Testing Locally Before Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Open browser to http://localhost:8501
```

---

## 🐛 Troubleshooting

**Large Model Files:**
- Use Git LFS for files > 100 MB
- Consider cloud storage (AWS S3, Google Cloud Storage) and download on startup

**Memory Issues:**
- Increase server resources
- Optimize model loading with lazy loading
- Use model compression techniques

**Deployment Fails:**
- Check logs: `streamlit run app.py --logger.level=debug`
- Verify all dependencies in requirements.txt
- Ensure Python version compatibility (3.9-3.11 recommended)

---

## 📝 Post-Deployment Checklist

- [ ] Test all features (website analysis, image detection, fake news)
- [ ] Check model loading and predictions
- [ ] Verify web scraping functionality works
- [ ] Monitor resource usage
- [ ] Set up error logging
- [ ] Configure custom domain (optional)

---

## 💡 Recommended: Start with Streamlit Cloud

For beginners, **Streamlit Cloud** is the easiest option:
- No infrastructure management
- Automatic scaling
- Free tier available
- Direct GitHub integration
- Easy updates (just push to GitHub)

Good luck with your deployment! 🚀
