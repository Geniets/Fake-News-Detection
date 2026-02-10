# Gemini API Setup Guide

## 🔑 Getting Your Free Gemini API Key

The AI Detection Suite now uses Google's Gemini 2.0 Flash Lite model for fake news detection. This provides better accuracy, faster results, and eliminates the need for large model downloads.

### Step 1: Get Your API Key

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign In**
   - Use your Google account
   - Accept the terms of service if prompted

3. **Create API Key**
   - Click "Create API Key" button
   - Select "Create API key in new project" (or choose existing project)
   - Copy the generated API key (starts with `AIza...`)
   - **Important:** Save this key securely - you won't be able to see it again!

### Step 2: Use in the App

**Option A: Enter in Sidebar (Recommended for Testing)**
1. Run the app
2. Look for "Gemini API Key" input in the left sidebar
3. Paste your API key
4. Status will show "Gemini API: Connected" when successful
5. Navigate to "News Analysis" tab to start detecting fake news

**Option B: Environment Variable (For Production)**
```bash
# On Linux/Mac
export GEMINI_API_KEY="your-api-key-here"

# On Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# On Windows CMD
set GEMINI_API_KEY=your-api-key-here
```

**Option C: Streamlit Secrets (For Streamlit Cloud)**
1. In your Streamlit Cloud dashboard
2. Go to your app settings
3. Click "Secrets"
4. Add:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

### Step 3: Test the Feature

1. Go to **"News Analysis"** tab
2. Paste a news article or upload a .txt file
3. Click **"Analyze Article"**
4. Wait for Gemini AI to analyze (usually 2-5 seconds)
5. Review the verdict, confidence score, and reasoning

## 📊 What You Get

The Gemini-powered analysis provides:
- ✅ **Verdict:** LEGITIMATE, FAKE, or MISLEADING
- 📈 **Confidence Score:** Percentage with visual progress bar
- 🧠 **AI Reasoning:** Clear explanation of the verdict
- 🚩 **Red Flags:** Specific concerning elements identified
- 💡 **Recommendation:** Actionable advice for users

## 🆓 Free Tier Limits

Google's free tier is generous:
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

For most use cases, this is more than enough!

## 🔒 API Key Security

**Best Practices:**
- ✅ Never commit API keys to GitHub
- ✅ Use environment variables or Streamlit secrets
- ✅ Rotate keys periodically
- ✅ Monitor usage in Google Cloud Console
- ❌ Don't share your API key publicly
- ❌ Don't hardcode keys in source code

## 🛠️ Troubleshooting

**"Gemini API: Failed" Error**
- Check if API key is correct (no extra spaces)
- Verify you've enabled the API at Google Cloud Console
- Ensure you're within the free tier limits

**"Rate Limit Exceeded"**
- You've exceeded 60 requests/minute
- Wait 1 minute and try again
- Consider upgrading to paid tier for higher limits

**No Response from API**
- Check your internet connection
- Verify API key is still valid
- Try regenerating the API key

## 📚 Additional Resources

- **Gemini API Documentation:** https://ai.google.dev/docs
- **Google AI Studio:** https://aistudio.google.com/
- **Pricing & Quotas:** https://ai.google.dev/pricing
- **API Key Management:** https://console.cloud.google.com/apis/credentials

## 💬 Support

If you encounter issues:
1. Check error message in the app (expand "Error Details")
2. Verify API key is correct
3. Check Google Cloud Console for API status
4. Review usage quotas

---

**Happy Fact-Checking! 🎯**
