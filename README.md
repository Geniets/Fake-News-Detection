# AI Detection Suite

A comprehensive multi-model platform for detecting fake news, AI-generated images, and analyzing website credibility using machine learning and AI.

## 🎯 Features

### 1. **Fake News Detection** (Powered by Groq AI)
- Analyzes news articles for misinformation
- Uses Groq's llama-3.3-70b-versatile model
- Provides detailed verdict, confidence score, reasoning, and red flags
- High-performance AI inference
- Secure API key configuration via environment variables
- **Note:** Training data may not be up-to-date; quick web search recommended for recent events

### 2. **Website Credibility Analysis**
- Evaluates website trustworthiness using 67 features
- 85% accuracy with Extra Trees Classifier
- Automatic metadata extraction from URLs
- Batch analysis support

### 3. **AI Image Detection**
- Identifies AI-generated vs. authentic images
- ResNet50-based deep learning model
- Detects synthetic patterns and artifacts

## 📁 Project Structure

```
AI-Detection-Suite/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version (3.11.9)
├── packages.txt                # System packages for deployment
├── .gitignore                  # Git ignore rules
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── GROQ_SETUP.md          # Groq API setup instructions
│
├── models/                     # Machine learning models
│   ├── stacking_model.joblib  # Website credibility model
│   ├── feature_names.joblib   # Feature names for ML model
│   ├── model_metadata.json    # Model metadata
│   ├── resnet50_best_FIXED.keras  # Image detection model
│   ├── config.joblib          # Model configuration
│   └── tokenizer.joblib       # Tokenizer (legacy)
│
├── data/                       # Data files
│   ├── trusted_sources_original.csv
│   ├── untrusted_sources.csv
│   └── website_metadata_examples.csv
│
├── utils/                      # Utility modules
│   ├── webscraper.py          # Website metadata scraper
│   ├── check_features.py      # Feature checking utilities
│   ├── debug_features.py      # Debugging tools
│   └── analyze_trusted.py     # Data analysis scripts
│
├── tests/                      # Test files
│   ├── test_model_bias.py     # Model bias tests
│   └── test_whois.py          # WHOIS functionality tests
│
├── notebooks/                  # Jupyter notebooks
│   └── modelling_realistic.ipynb  # Model development notebook
│
├── archive/                    # Archived datasets
│   ├── README
│   └── *.tsv
│
└── saved_models/               # Backup/alternative models
    └── (model backups)
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Groq API Key
1. Visit: https://console.groq.com/
2. Sign up or sign in
3. Create an API key
4. Copy the key

### 3. Set Environment Variable

**For Production (Streamlit Cloud):**
- Add to Streamlit Secrets:
  ```toml
  GROQ_API_KEY = "your-groq-api-key-here"
  ```

**For Local Development:**
```bash
# Create .env file
GROQ_API_KEY=your_groq_api_key_here

# Or set in terminal
export GROQ_API_KEY="your-groq-api-key-here"
```

### 4. Run the App
```bash
streamlit run app.py
```

### 5. Start Analyzing
- Check sidebar for "Groq API Status: Connected"
- Navigate to News Analysis tab
- Start analyzing news, websites, and images!

## 📊 Model Performance

### Website Credibility Model
- **Accuracy:** 85.00%
- **F1-Score:** 0.8370
- **Type:** Stacking Ensemble (Extra Trees)
- **Features:** 67 engineered features

### AI Image Detection Model
- **Architecture:** ResNet50
- **Input:** 224x224 RGB images
- **Classes:** Real vs. AI-generated

### Fake News Detection (Gemini AI)
- **Model:** Gemini 2.0 Flash Lite
- **Speed:** 2-5 seconds per analysis
- **Free Tier:** 60 req/min, 1,500 req/day

## 🔧 Configuration Files

- **requirements.txt** - Python package dependencies
- **runtime.txt** - Python version specification (3.11.9)
- **packages.txt** - System-level packages for Streamlit Cloud
- **.gitignore** - Excludes large model files and cache

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Complete deployment instructions
- [Gemini Setup](docs/GEMINI_SETUP.md) - API key setup and troubleshooting

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy `app.py`

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🛠️ Utility Scripts

Located in `utils/`:
- **webscraper.py** - Extracts metadata from URLs
- **check_features.py** - Validates feature engineering
- **debug_features.py** - Debugging model inputs
- **analyze_trusted.py** - Analyzes trusted source patterns

## 🧪 Testing

Run tests from the `tests/` directory:
```bash
python tests/test_model_bias.py
python tests/test_whois.py
```

## 📦 Dependencies

### Core
- streamlit >= 1.28.0
- numpy == 1.26.4
- scikit-learn == 1.5.2
- pandas == 2.2.3

### Deep Learning
- keras == 3.3.3
- tensorflow == 2.15.1

### AI API
- google-generativeai >= 0.3.0

### Web Scraping
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- python-whois >= 0.8.0

## 🔐 Security

- **API Keys:** Never commit to Git
- **Use:** Streamlit Secrets or environment variables
- **Rotate:** Keys periodically
- **Monitor:** Usage in Google Cloud Console

## 📝 License

This project is for educational and research purposes.

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues or questions:
1. Check [docs/GEMINI_SETUP.md](docs/GEMINI_SETUP.md) for API troubleshooting
2. Review [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment issues
3. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Add more AI detection models
- [ ] Implement user authentication
- [ ] Add result export functionality
- [ ] Create REST API endpoints
- [ ] Add multi-language support

---

**Built with ❤️ using Streamlit, TensorFlow, and Google Gemini AI**

Version: 2.0 | Last Updated: February 2026
