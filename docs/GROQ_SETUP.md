# Groq API Setup Guide

## 🔑 Getting Your Groq API Key

The AI Detection Suite uses Groq's **llama-3.3-70b-versatile** model for fake news detection. This provides high-performance AI analysis with fast inference times.

### Step 1: Get Your API Key

1. **Visit Groq Console**
   - Go to: https://console.groq.com/

2. **Sign Up / Sign In**
   - Create an account or sign in
   - Complete the registration process

3. **Create API Key**
   - Navigate to the API Keys section
   - Click "Create API Key"
   - Give it a descriptive name (e.g., "Fake News Detection")
   - Copy the generated API key
   - **Important:** Save this key securely - you won't be able to see it again!

### Step 2: Configure the Environment Variable

The app reads the API key from the `GROQ_API_KEY` environment variable for security.

**For Production Deployment (Streamlit Cloud):**
1. In your Streamlit Cloud dashboard
2. Go to your app settings
3. Click "Secrets"
4. Add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
5. Save and restart the app

**For Local Development:**

Create a `.env` file in the project root (see `.env.example`):
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or set it in your terminal:

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=your-groq-api-key-here
```

**For Docker:**
```bash
docker run -e GROQ_API_KEY="your-groq-api-key-here" your-image
```

**For Heroku:**
```bash
heroku config:set GROQ_API_KEY="your-groq-api-key-here"
```

### Step 3: Verify Connection

1. Run the app
2. Check the sidebar - look for "Fake News Detection (AI-Powered)" section
3. You should see "Status: Connected" if the API key is configured correctly
4. If you see "Status: Not Connected", verify:
   - The environment variable is set correctly
   - The API key is valid
   - You've restarted the app after setting the variable

### Step 4: Start Analyzing

1. Navigate to the "News Analysis" tab
2. Paste article text or upload a .txt file
3. Click "Analyze Article"
4. Review the AI-powered analysis results

## 🔧 Troubleshooting

**"GROQ_API_KEY environment variable not set"**
- Make sure you've set the environment variable correctly
- Restart the application after setting the variable
- For Streamlit Cloud, ensure it's in the Secrets section

**"Status: Not Connected"**
- Verify the API key is correct (no extra spaces or quotes)
- Check that your Groq account is active
- Ensure you have API credits/quota available

**API Errors During Analysis**
- Check your Groq API usage limits
- Verify your API key hasn't been revoked
- Ensure you have a stable internet connection

## 📊 API Limits

Groq offers generous free tier limits:
- Check your current plan at: https://console.groq.com/
- Monitor your usage in the Groq dashboard
- Upgrade if you need higher limits

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Add `.env` to your `.gitignore`
   - Use environment variables for production

2. **Rotate keys periodically**
   - Generate new keys every few months
   - Delete unused keys from Groq console

3. **Use Streamlit Secrets for deployment**
   - Keeps keys secure and separate from code
   - Easy to update without code changes

4. **Monitor API usage**
   - Check Groq dashboard regularly
   - Set up alerts if available

## 🎯 Why Groq?

- ⚡ **Ultra-fast inference** - Faster than traditional cloud AI
- 💪 **Powerful models** - Access to Llama 3.3 70B
- 💰 **Cost-effective** - Competitive pricing
- 🔧 **Easy integration** - OpenAI-compatible API
- 📊 **Reliable** - High uptime and performance

---

**Need Help?**
- Groq Documentation: https://console.groq.com/docs
- Groq Discord: Check the Groq website for community links
