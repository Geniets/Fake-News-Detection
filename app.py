import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
from utils.webscraper import scrape_website_metadata, format_metadata_for_display
from PIL import Image
import io
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="AI Detection Suite",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1f1f1f;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Load website credibility model
@st.cache_resource
def load_website_model():
    try:
        model = joblib.load('stacking_model.joblib')
        features = joblib.load('feature_names.joblib')
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # Fix: Use only the features the model was trained on
        # The model expects 67 features but feature_names.joblib has 82
        n_features_expected = model.n_features_in_
        if len(features) > n_features_expected:
            features = features[:n_features_expected]

        
        return model, features, metadata, True
    except Exception as e:
        return None, None, None, False

# Load AI image detection model
@st.cache_resource
def load_image_model():
    try:
        import keras  # Keras 3.x is standalone, not from tensorflow
        import warnings
        warnings.filterwarnings('ignore')
        
        # Load the Keras model (.keras file is a zip format in Keras 3.x)
        # Using FIXED version with data_format parameter removed from RandomFlip
        model = keras.models.load_model('models/resnet50_best_FIXED.keras')
        
        return model, True
    except Exception as e:
        # Store error message for display
        error_msg = str(e)
        if "batch_normalization" in error_msg.lower() or "input" in error_msg.lower():
            st.session_state['image_model_error'] = "Keras version mismatch: Model requires Keras 3.x"
        else:
            st.session_state['image_model_error'] = f"Error: {error_msg[:200]}"
        return None, False

# Download large model from Google Drive if not present
# Initialize Gemini API
def initialize_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        return True, None
    except Exception as e:
        return False, str(e)

# Load all models
website_model, feature_names, model_info, website_model_loaded = load_website_model()
image_model, image_model_loaded = load_image_model()

# Header
st.markdown('<h1 class="main-header">AI Detection Suite</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Model Analysis Platform for Website Credibility and Image Authenticity</p>', unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### Model Information")
    st.divider()
    
    # Website Model Status
    st.markdown("#### Website Credibility Model")
    if website_model_loaded:
        st.success("Status: Loaded")
        st.caption("Model ready for analysis")
    else:
        st.error("Status: Not Loaded")
        st.caption("Check if models/stacking_model.joblib exists")
    
    st.divider()
    
    # Image Model Status
    st.markdown("#### AI Image Detection Model")
    if image_model_loaded:
        st.success("Status: Loaded")
        st.caption("Model ready for predictions")
    else:
        st.error("Status: Not Loaded")
        if 'image_model_error' in st.session_state:
            st.caption(st.session_state['image_model_error'])
        st.info("""
        **Issue:** The model was saved with Keras 3.10.0 but we have Keras 2.15.0
        
        **Solution:** Ask your friend to export the model in Keras 2.x compatible format or provide:
        - Model as .h5 file (legacy format)
        - Or upgrade to Keras 3.x (requires TensorFlow 2.16+)
        """)
    
    st.divider()
    
    # Gemini API Configuration
    st.markdown("#### Fake News Detection (Gemini AI)")
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Enter your Google Gemini API key. Get one at https://makersuite.google.com/app/apikey",
        key="gemini_api_key"
    )
    
    if gemini_api_key:
        if 'gemini_initialized' not in st.session_state or st.session_state.get('gemini_key') != gemini_api_key:
            success, error = initialize_gemini(gemini_api_key)
            st.session_state['gemini_initialized'] = success
            st.session_state['gemini_key'] = gemini_api_key
            if success:
                st.success("Gemini API: Connected")
            else:
                st.error(f"Gemini API: Failed - {error}")
        else:
            if st.session_state.get('gemini_initialized'):
                st.success("Gemini API: Connected")
    else:
        st.info("Enter API key to enable fake news detection")
        st.session_state['gemini_initialized'] = False
    
    st.divider()
    st.caption("AI Detection Suite v2.0")
    st.caption("Multi-Model Analysis Platform")

# Main content
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "URL Analysis", 
    "Manual Entry", 
    "Batch Prediction",
    "Image Detection",
    "News Analysis",
    "Model Information",
    "Documentation"
])

# Tab 1: URL Scraper
with tab1:
    st.markdown("### Automatic Website Analysis")
    st.markdown("Enter a website URL to automatically extract metadata and analyze credibility.")
    st.markdown("")
    st.markdown("")
    
    url_input = st.text_input("Enter Website URL", placeholder="https://example.com", key="url_input")
    
    col_scrape1, col_scrape2 = st.columns([1, 3])
    with col_scrape1:
        scrape_button = st.button("Analyze Website", type="primary", use_container_width=True)
    
    if scrape_button and url_input:
        with st.spinner(f"Analyzing {url_input}..."):
            # Scrape website
            scraped_data = scrape_website_metadata(url_input)
            
            if 'error' in scraped_data:
                st.error(f"Error: {scraped_data['error']}")
            else:
                st.success(f"Successfully analyzed {scraped_data.get('domain', url_input)}")
                
                # Show debug info if available
                if 'debug_info' in scraped_data and scraped_data['debug_info']:
                    with st.expander("Debug Information", expanded=False):
                        for info in scraped_data['debug_info']:
                            st.text(info)
                
                # Display scraped metadata
                with st.expander("View Extracted Metadata", expanded=True):
                    col_meta1, col_meta2, col_meta3 = st.columns(3)
                    
                    with col_meta1:
                        st.markdown("**Security**")
                        st.write(f"HTTPS: {'Yes' if scraped_data.get('has_https') == 'Yes' else 'No'}")
                        st.write(f"SSL Valid: {'Yes' if scraped_data.get('ssl_valid') == 'Yes' else 'No'}")
                        st.write(f"SSL Issuer: {scraped_data.get('ssl_issuer', 'Unknown')}")
                        st.write(f"TLS: {scraped_data.get('tls_version', 'N/A')}")
                        st.write(f"Cert Type: {scraped_data.get('certificate_type', 'N/A')}")
                    
                    with col_meta2:
                        st.markdown("**Domain & Performance**")
                        st.write(f"Domain Age: {scraped_data.get('domain_age_years', 0)} yrs")
                        if scraped_data.get('domain_age_years', 0) == 0:
                            st.caption("Could not retrieve domain age")
                        st.write(f"Registrar: {scraped_data.get('domain_registrar', 'Unknown')}")
                        st.write(f"Load Time: {scraped_data.get('page_load_time_sec', 0)}s")
                        st.write(f"Redirects: {scraped_data.get('redirect_count', 0)}")
                        st.write(f"Response: {scraped_data.get('server_response_code', 'N/A')}")
                    
                    with col_meta3:
                        st.markdown("**Content & Trust**")
                        st.write(f"Ads Density: {scraped_data.get('ads_density_score', 0):.2f}")
                        st.write(f"External Links: {scraped_data.get('external_links_count', 0)}")
                        st.write(f"Contact Info: {'Available' if scraped_data.get('contact_info_available') else 'Missing'}")
                        st.write(f"Privacy Policy: {'Present' if scraped_data.get('privacy_policy_exists') else 'Missing'}")
                        st.write(f"Mobile: {scraped_data.get('mobile_responsive', 'No')}")
                
                # Make prediction
                if website_model_loaded:
                    with st.spinner("Making prediction..."):
                        # Convert scraped data to DataFrame
                        # Calculate domain age bucket
                        domain_age = scraped_data.get('domain_age_years', 0.0)
                        if domain_age < 1:
                            domain_age_bucket = '0-1y'
                        elif domain_age < 5:
                            domain_age_bucket = '1-5y'
                        elif domain_age < 10:
                            domain_age_bucket = '5-10y'
                        elif domain_age < 20:
                            domain_age_bucket = '10-20y'
                        else:
                            domain_age_bucket = '20y+'
                        
                        input_data = {
                            'has_https': scraped_data.get('has_https', 'No'),
                            'ssl_valid': scraped_data.get('ssl_valid', 'No'),
                            'ssl_issuer': scraped_data.get('ssl_issuer', 'Unknown'),
                            'tls_version': scraped_data.get('tls_version', 'none'),
                            'certificate_type': scraped_data.get('certificate_type', 'none'),
                            'domain_age_years': domain_age,
                            'domain_age_bucket': domain_age_bucket,
                            'domain_registrar': scraped_data.get('domain_registrar', 'Unknown'),
                            'whois_privacy_enabled': scraped_data.get('whois_privacy_enabled', False),
                            'page_load_time_sec': scraped_data.get('page_load_time_sec', 0.0),
                            'redirect_count': scraped_data.get('redirect_count', 0),
                            'server_response_code': scraped_data.get('server_response_code', 404),
                            'ads_density_score': scraped_data.get('ads_density_score', 0.0),
                            'external_links_count': scraped_data.get('external_links_count', 0),
                            'popups_present': scraped_data.get('popups_present', 'No'),
                            'server_location': scraped_data.get('server_location', 'Unknown'),
                            'hosting_type': scraped_data.get('hosting_type', 'shared'),
                            'cdn_used': scraped_data.get('cdn_used', 'no'),
                            'contact_info_available': scraped_data.get('contact_info_available', False),
                            'privacy_policy_exists': scraped_data.get('privacy_policy_exists', False),
                            'terms_of_service_exists': scraped_data.get('terms_of_service_exists', False),
                            'social_media_presence': scraped_data.get('social_media_presence', 'low'),
                            'content_update_frequency': scraped_data.get('content_update_frequency', 'irregular'),
                            'mobile_responsive': scraped_data.get('mobile_responsive', 'No')
                        }
                        
                        df_scraped = pd.DataFrame([input_data])
                        
                        # Get encoded features with one-hot encoding
                        df_encoded = pd.get_dummies(df_scraped)
                        
                        # Create a dataframe with all required features
                        df_final = pd.DataFrame(0, index=[0], columns=feature_names)
                        
                        # Fill in the features that we have
                        for col in df_encoded.columns:
                            if col in feature_names:
                                df_final[col] = df_encoded[col].values[0]
                        
                        # Ensure we have exactly the right number of features
                        if len(df_final.columns) != website_model.n_features_in_:
                            st.error(f"Feature mismatch: {len(df_final.columns)} provided, {website_model.n_features_in_} expected")
                            st.stop()
                        
                        # Make prediction
                        prediction = website_model.predict(df_final)[0]
                        prediction_proba = website_model.predict_proba(df_final)[0]
                        
                        # Display result
                        st.divider()
                        st.markdown("### Analysis Result")
                        
                        col_result1, col_result2 = st.columns([1, 2])
                        
                        with col_result1:
                            if prediction == 1:
                                st.success("**TRUSTED WEBSITE**")
                                st.metric("Confidence Level", f"{prediction_proba[1]*100:.1f}%")
                            else:
                                st.error("**UNTRUSTED WEBSITE**")
                                st.metric("Confidence Level", f"{prediction_proba[0]*100:.1f}%")
                        
                        with col_result2:
                            st.markdown("**Probability Distribution**")
                            conf_df = pd.DataFrame({
                                'Classification': ['Untrusted', 'Trusted'],
                                'Probability': [prediction_proba[0]*100, prediction_proba[1]*100]
                            })
                            st.bar_chart(conf_df.set_index('Classification'))
                        
                        # Key factors
                        st.markdown("### Key Analysis Factors")
                        factors_col1, factors_col2 = st.columns(2)
                        
                        with factors_col1:
                            st.markdown("**Positive Indicators**")
                            positive = []
                            if scraped_data.get('has_https') == 'Yes':
                                positive.append("HTTPS encryption enabled")
                            if scraped_data.get('ssl_valid') == 'Yes':
                                positive.append("Valid SSL certificate")
                            if scraped_data.get('domain_age_years', 0) >= 5:
                                positive.append(f"Established domain ({scraped_data.get('domain_age_years')} years)")
                            if scraped_data.get('contact_info_available'):
                                positive.append("Contact information available")
                            if scraped_data.get('privacy_policy_exists'):
                                positive.append("Privacy policy present")
                            if scraped_data.get('cdn_used') == 'yes':
                                positive.append("Content delivery network in use")
                            
                            if positive:
                                for item in positive:
                                    st.markdown(f"- {item}")
                            else:
                                st.markdown("*No significant positive indicators detected*")
                        
                        with factors_col2:
                            st.markdown("**Risk Indicators**")
                            negative = []
                            if scraped_data.get('has_https') == 'No':
                                negative.append("Missing HTTPS encryption")
                            if scraped_data.get('ssl_valid') == 'No':
                                negative.append("Invalid SSL certificate")
                            if scraped_data.get('domain_age_years', 0) < 1:
                                negative.append("Recently registered domain")
                            if scraped_data.get('ads_density_score', 0) > 0.3:
                                negative.append(f"High advertisement density ({scraped_data.get('ads_density_score'):.2f})")
                            if not scraped_data.get('contact_info_available'):
                                negative.append("No contact information found")
                            if not scraped_data.get('privacy_policy_exists'):
                                negative.append("No privacy policy found")
                            if scraped_data.get('popups_present') == 'Yes':
                                negative.append("Popup elements detected")
                            
                            if negative:
                                for item in negative:
                                    st.markdown(f"- {item}")
                            else:
                                st.markdown("*No significant risk indicators detected*")
    
    elif scrape_button and not url_input:
        st.warning("Please enter a URL to analyze")

# Tab 2: Manual Entry
with tab2:
    st.markdown("### Manual Website Analysis")
    st.markdown("Manually enter website metadata for credibility assessment.")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Security Features")
        has_https = st.selectbox("Has HTTPS?", ["Yes", "No"])
        ssl_valid = st.selectbox("SSL Valid?", ["Yes", "No"])
        ssl_issuer = st.selectbox("SSL Issuer", ["Let's Encrypt", "DigiCert", "GlobalSign", "Comodo", "GeoTrust", "Self-signed", "Unknown", "Cloudflare"])
        tls_version = st.selectbox("TLS Version", ["TLS 1.3", "TLS 1.2", "TLS 1.1", "TLS 1.0", "none"])
        certificate_type = st.selectbox("Certificate Type", ["EV", "OV", "DV", "none", "self_signed"])
        
        st.subheader("Domain Information")
        domain_age = st.number_input("Domain Age (years)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
        domain_registrar = st.selectbox("Domain Registrar", ["CSC Corporate", "Network Solutions", "MarkMonitor", "Verisign", "Namecheap", "GoDaddy", "eNom", "Unknown"])
        whois_privacy = st.checkbox("WHOIS Privacy Enabled")
        
    with col2:
        st.subheader("Performance & Content")
        page_load_time = st.number_input("Page Load Time (sec)", min_value=0.0, max_value=30.0, value=2.0, step=0.1)
        redirect_count = st.number_input("Redirect Count", min_value=0, max_value=10, value=0)
        response_code = st.selectbox("Server Response Code", [200, 301, 302, 404])
        ads_density = st.slider("Ads Density Score", 0.0, 1.0, 0.2, 0.05)
        external_links = st.number_input("External Links Count", min_value=0, max_value=500, value=50)
        popups = st.selectbox("Popups Present?", ["No", "Yes"])
        
        st.subheader("Infrastructure")
        server_location = st.selectbox("Server Location", ["USA", "UK", "Canada", "EU", "France", "Offshore", "Russia", "Unknown", "Asia"])
        hosting_type = st.selectbox("Hosting Type", ["enterprise", "cloud", "dedicated", "shared", "offshore"])
        cdn_used = st.selectbox("CDN Used?", ["yes", "no"])
        
    st.subheader("Additional Information")
    col3, col4 = st.columns(2)
    
    with col3:
        contact_info = st.checkbox("Contact Info Available", value=True)
        privacy_policy = st.checkbox("Privacy Policy Exists", value=True)
        terms_of_service = st.checkbox("Terms of Service Exists", value=True)
        
    with col4:
        social_media = st.selectbox("Social Media Presence", ["high", "medium", "low"])
        content_update = st.selectbox("Content Update Frequency", ["hourly", "daily", "weekly", "irregular", "monthly"])
        mobile_responsive = st.selectbox("Mobile Responsive?", ["Yes", "No", "Partial"])
    
    if st.button("Check Credibility", type="primary", use_container_width=True):
        if website_model_loaded:
            # Calculate domain age bucket
            if domain_age < 1:
                domain_age_bucket = '0-1y'
            elif domain_age < 5:
                domain_age_bucket = '1-5y'
            elif domain_age < 10:
                domain_age_bucket = '5-10y'
            elif domain_age < 20:
                domain_age_bucket = '10-20y'
            else:
                domain_age_bucket = '20y+'
            
            # Create input dataframe
            input_data = pd.DataFrame({
                'has_https': [has_https],
                'ssl_valid': [ssl_valid],
                'ssl_issuer': [ssl_issuer],
                'tls_version': [tls_version],
                'certificate_type': [certificate_type],
                'domain_age_years': [domain_age],
                'domain_age_bucket': [domain_age_bucket],
                'domain_registrar': [domain_registrar],
                'whois_privacy_enabled': [whois_privacy],
                'page_load_time_sec': [page_load_time],
                'redirect_count': [redirect_count],
                'server_response_code': [response_code],
                'ads_density_score': [ads_density],
                'external_links_count': [external_links],
                'popups_present': [popups],
                'server_location': [server_location],
                'hosting_type': [hosting_type],
                'cdn_used': [cdn_used],
                'contact_info_available': [contact_info],
                'privacy_policy_exists': [privacy_policy],
                'terms_of_service_exists': [terms_of_service],
                'social_media_presence': [social_media],
                'content_update_frequency': [content_update],
                'mobile_responsive': [mobile_responsive]
            })
            
            # One-hot encode categorical features
            input_encoded = pd.get_dummies(input_data)
            
            # Create a dataframe with all required features
            input_final = pd.DataFrame(0, index=[0], columns=feature_names)
            
            # Fill in the features that we have
            for col in input_encoded.columns:
                if col in feature_names:
                    input_final[col] = input_encoded[col].values[0]
            
            # Validate feature count
            if len(input_final.columns) != website_model.n_features_in_:
                st.error(f"Feature mismatch: {len(input_final.columns)} provided, {website_model.n_features_in_} expected")
                st.stop()
            
            # Make prediction
            prediction = website_model.predict(input_final)[0]
            probability = website_model.predict_proba(input_final)[0]
            
            # Display results
            st.divider()
            st.markdown("### Analysis Results")
            
            col_result1, col_result2, col_result3 = st.columns([1, 2, 1])
            
            with col_result2:
                if prediction == 1:
                    st.success("**TRUSTED WEBSITE**")
                    confidence = probability[1] * 100
                    st.metric("Confidence Level", f"{confidence:.1f}%")
                    st.progress(confidence/100)
                    
                    st.info("""
                    **Assessment Summary:**
                    
                    This website demonstrates strong credibility indicators including robust security features, 
                    professional infrastructure, and transparent operational policies.
                    """)
                else:
                    st.error("**UNTRUSTED WEBSITE**")
                    confidence = probability[0] * 100
                    st.metric("Confidence Level", f"{confidence:.1f}%")
                    st.progress(confidence/100)
                    
                    st.warning("""
                    **Assessment Summary:**
                    
                    This website exhibits characteristics commonly associated with low credibility sources, 
                    including weak security indicators, questionable infrastructure, or missing transparency features.
                    """)
                
                # Show probability breakdown
                st.divider()
                st.markdown("**Probability Distribution**")
                prob_df = pd.DataFrame({
                    'Classification': ['Untrusted', 'Trusted'],
                    'Probability': [probability[0]*100, probability[1]*100]
                })
                st.bar_chart(prob_df.set_index('Classification'))
        else:
            st.error("Model not loaded. Please check model files.")

# Tab 3: Batch Prediction
with tab3:
    st.markdown("### Batch Website Analysis")
    st.markdown("Upload a CSV file to analyze multiple websites simultaneously.")
    st.divider()
    
    st.info("""
    Upload a CSV file with website metadata. The file should contain the following columns:
    `has_https`, `ssl_valid`, `ssl_issuer`, `tls_version`, `certificate_type`, `domain_age_years`,
    `domain_registrar`, `whois_privacy_enabled`, `page_load_time_sec`, `redirect_count`,
    `server_response_code`, `ads_density_score`, `external_links_count`, `popups_present`,
    `server_location`, `hosting_type`, `cdn_used`, `contact_info_available`, `privacy_policy_exists`,
    `terms_of_service_exists`, `social_media_presence`, `content_update_frequency`, `mobile_responsive`
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            batch_data = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(batch_data)} records")
            
            # Show preview
            with st.expander("Preview Data"):
                st.dataframe(batch_data.head())
            
            if st.button("Run Batch Prediction", type="primary"):
                if website_model_loaded:
                    # Calculate domain age bucket if not present
                    if 'domain_age_bucket' not in batch_data.columns:
                        batch_data['domain_age_bucket'] = pd.cut(
                            batch_data['domain_age_years'],
                            bins=[-np.inf, 1, 5, 10, 20, np.inf],
                            labels=['0-1y', '1-5y', '5-10y', '10-20y', '20y+']
                        )
                    
                    # One-hot encode
                    batch_encoded = pd.get_dummies(batch_data)
                    
                    # Create a dataframe with all required features
                    batch_final = pd.DataFrame(0, index=range(len(batch_data)), columns=feature_names)
                    
                    # Fill in the features that we have
                    for col in batch_encoded.columns:
                        if col in feature_names:
                            batch_final[col] = batch_encoded[col].values
                    
                    # Validate feature count
                    if len(batch_final.columns) != website_model.n_features_in_:
                        st.error(f"Feature mismatch: {len(batch_final.columns)} provided, {website_model.n_features_in_} expected")
                        st.stop()
                    
                    # Predict
                    predictions = website_model.predict(batch_final)
                    probabilities = website_model.predict_proba(batch_final)
                    
                    # Add results to dataframe
                    batch_data['Prediction'] = ['Trusted' if p == 1 else 'Untrusted' for p in predictions]
                    batch_data['Confidence'] = [max(prob)*100 for prob in probabilities]
                    batch_data['Trust_Probability'] = [prob[1]*100 for prob in probabilities]
                    
                    # Display results
                    st.success("Predictions completed!")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Websites", len(batch_data))
                    with col2:
                        trusted_count = (predictions == 1).sum()
                        st.metric("Trusted", trusted_count)
                    with col3:
                        untrusted_count = (predictions == 0).sum()
                        st.metric("Untrusted", untrusted_count)
                    
                    # Show results
                    st.markdown("### Analysis Results")
                    st.dataframe(
                        batch_data[['Prediction', 'Confidence', 'Trust_Probability']].style.format({
                            'Confidence': '{:.1f}%',
                            'Trust_Probability': '{:.1f}%'
                        })
                    )
                    
                    # Download results
                    csv = batch_data.to_csv(index=False)
                    st.download_button(
                        label="Download Results CSV",
                        data=csv,
                        file_name="website_credibility_predictions.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.error("Model not loaded. Please check model files.")
                    
        except Exception as e:
            st.error(f"Error processing file: {e}")

# Tab 4: AI Image Detection
with tab4:
    st.markdown("### AI-Generated Image Detection")
    st.markdown("Upload an image to determine if it was generated by artificial intelligence or is an authentic photograph.")
    st.divider()
    
    if not image_model_loaded:
        st.warning("""
        **Image AI Detection Model Not Loaded**
        
        To enable this feature:
        1. Place your friend's image detection model file in the project directory
        2. Name it `resnet50_best.joblib`
        3. Restart the application
        
        The model should accept image data and return predictions for AI-generated vs. real images.
        """)
    else:
        col_upload, col_info = st.columns([2, 1])
        
        with col_upload:
            uploaded_image = st.file_uploader(
                "Choose an image file",
                type=["jpg", "jpeg", "png", "bmp", "webp"],
                help="Supported formats: JPG, JPEG, PNG, BMP, WEBP"
            )
            
            if uploaded_image is not None:
                # Display the image
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Image information
                st.caption(f"Image size: {image.size[0]}x{image.size[1]} pixels | Format: {image.format}")
        
        with col_info:
            st.markdown("**Analysis Information**")
            st.write("This model analyzes:")
            st.write("- Visual patterns")
            st.write("- Artifact detection")
            st.write("- Metadata analysis")
            st.write("- Statistical properties")
        
        if uploaded_image is not None:
            if st.button("Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    try:
                        # Preprocess image for ResNet50 model
                        # ResNet50 expects 224x224 RGB images
                        image = Image.open(uploaded_image)
                        
                        # Convert to RGB if needed
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # Resize to 224x224 (ResNet50 input size)
                        image_resized = image.resize((224, 224))
                        
                        # Convert to numpy array
                        img_array = np.array(image_resized)
                        
                        # Normalize to [0, 1] range
                        img_array = img_array / 255.0
                        
                        # Add batch dimension: (1, 224, 224, 3)
                        img_array = np.expand_dims(img_array, axis=0)
                        
                        # Make prediction
                        prediction = image_model.predict(img_array, verbose=0)
                        
                        # Model uses sigmoid activation (single output)
                        # Output is probability of AI-generated (0=Real, 1=AI)
                        ai_probability = float(prediction[0][0])
                        real_probability = 1 - ai_probability
                        predicted_class = 1 if ai_probability > 0.5 else 0
                        confidence = max(ai_probability, real_probability) * 100
                        
                        # Display results
                        st.divider()
                        st.markdown("### Detection Results")
                        
                        col_res1, col_res2 = st.columns([1, 2])
                        
                        with col_res1:
                            # predicted_class: 0 = Real, 1 = AI-generated
                            if predicted_class == 1:
                                st.error("**AI-GENERATED IMAGE**")
                                st.metric("Confidence Level", f"{confidence:.1f}%")
                            else:
                                st.success("**AUTHENTIC IMAGE**")
                                st.metric("Confidence Level", f"{confidence:.1f}%")
                        
                        with col_res2:
                            st.markdown("**Probability Distribution**")
                            prob_df = pd.DataFrame({
                                'Classification': ['Authentic', 'AI-Generated'],
                                'Probability': [real_probability*100, ai_probability*100]
                            })
                            st.bar_chart(prob_df.set_index('Classification'))
                        
                        # Additional insights
                        st.markdown("### Technical Analysis")
                        col_det1, col_det2 = st.columns(2)
                        
                        with col_det1:
                            st.markdown("**Image Properties**")
                            st.write(f"Dimensions: {image.size[0]} x {image.size[1]} pixels")
                            st.write(f"Color Mode: {image.mode}")
                            st.write(f"File Format: {image.format}")
                        
                        with col_det2:
                            st.markdown("**Analysis Interpretation**")
                            if predicted_class == 1:
                                st.write("This image exhibits characteristics typical of AI-generated content.")
                                st.write("")
                                st.write("Common indicators include synthetic patterns, unusual artifacts, and statistical anomalies.")
                            else:
                                st.write("This image appears to be an authentic photograph.")
                                st.write("")
                                st.write("Natural characteristics detected include authentic visual patterns, realistic noise distribution, and natural texture.")
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
                        import traceback
                        st.code(traceback.format_exc())
                        st.info("""
                        **Troubleshooting Tips:**
                        - Ensure the image is in a supported format (JPG, PNG, etc.)
                        - Try a different image
                        - Check that the model file is not corrupted
                        """)

# Tab 5: Fake News Detection with Gemini
with tab5:
    st.markdown("### Fake News Detection (Powered by Gemini AI)")
    st.markdown("Analyze news articles or text content to detect potential misinformation using advanced AI.")
    st.divider()
    
    if not st.session_state.get('gemini_initialized', False):
        st.warning("""
        **Gemini API Key Required**
        
        Please enter your Gemini API key in the sidebar to enable fake news detection.
        
        Get your free API key at: https://makersuite.google.com/app/apikey
        """)
    else:
        # Input method selection
        input_method = st.radio(
            "Select input method:",
            ["Paste Text", "Upload File"],
            horizontal=True
        )
        
        article_text = None
        
        if input_method == "Paste Text":
            article_text = st.text_area(
                "Enter article text or news content:",
                height=300,
                placeholder="Paste the article text here..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file",
                type=["txt"],
                help="Upload a .txt file containing the article"
            )
            if uploaded_file is not None:
                article_text = uploaded_file.read().decode("utf-8")
                st.text_area("Loaded content:", article_text, height=200, disabled=True)
        
        if st.button("Analyze Article", type="primary", use_container_width=True):
            if article_text and len(article_text.strip()) > 0:
                with st.spinner("Analyzing article with Gemini AI..."):
                    try:
                        # Initialize Gemini model
                        model = genai.GenerativeModel('gemini-2.0-flash-lite')
                        
                        # Create detailed prompt for fake news detection
                        prompt = f"""You are a professional fact-checker and misinformation analyst. Analyze the following article/text for signs of fake news, misinformation, or unreliable content.

Consider these factors:
1. Factual accuracy and verifiability
2. Source credibility indicators
3. Emotional manipulation or sensationalism
4. Logical consistency and reasoning
5. Use of credible citations or lack thereof
6. Bias, propaganda, or misleading framing
7. Writing quality and professionalism

Article to analyze:
{article_text}

Provide your analysis in this EXACT format:

VERDICT: [LEGITIMATE or FAKE or MISLEADING]
CONFIDENCE: [percentage as number only, e.g., 85]
REASONING: [2-3 sentence explanation of your verdict]
RED_FLAGS: [comma-separated list of concerning elements, or "None" if legitimate]
RECOMMENDATION: [specific action user should take]"""
                        
                        # Get response from Gemini
                        response = model.generate_content(prompt)
                        result_text = response.text
                        
                        # Parse response
                        lines = result_text.strip().split('\n')
                        verdict = "UNKNOWN"
                        confidence = 0
                        reasoning = ""
                        red_flags = ""
                        recommendation = ""
                        
                        for line in lines:
                            if line.startswith("VERDICT:"):
                                verdict = line.replace("VERDICT:", "").strip()
                            elif line.startswith("CONFIDENCE:"):
                                try:
                                    confidence = int(line.replace("CONFIDENCE:", "").strip().replace("%", ""))
                                except:
                                    confidence = 0
                            elif line.startswith("REASONING:"):
                                reasoning = line.replace("REASONING:", "").strip()
                            elif line.startswith("RED_FLAGS:"):
                                red_flags = line.replace("RED_FLAGS:", "").strip()
                            elif line.startswith("RECOMMENDATION:"):
                                recommendation = line.replace("RECOMMENDATION:", "").strip()
                        
                        # Display results
                        st.divider()
                        st.markdown("### Analysis Result")
                        
                        if "FAKE" in verdict.upper():
                            st.error(f"**🚨 {verdict} DETECTED**")
                        elif "MISLEADING" in verdict.upper():
                            st.warning(f"**⚠️ {verdict} CONTENT**")
                        else:
                            st.success(f"**✓ {verdict} NEWS**")
                        
                        # Confidence meter
                        st.markdown("### Confidence Level")
                        st.progress(confidence / 100)
                        st.write(f"**{confidence}%** confidence in this assessment")
                        
                        # Analysis details
                        st.markdown("### Analysis Details")
                        col_det1, col_det2 = st.columns(2)
                        
                        with col_det1:
                            st.markdown("**Content Statistics**")
                            word_count = len(article_text.split())
                            char_count = len(article_text)
                            st.write(f"Word Count: {word_count}")
                            st.write(f"Character Count: {char_count}")
                            st.write(f"Analysis Model: Gemini 2.0 Flash Lite")
                        
                        with col_det2:
                            st.markdown("**AI Reasoning**")
                            st.write(reasoning)
                        
                        # Red flags if any
                        if red_flags and red_flags.lower() != "none":
                            st.markdown("### 🚩 Red Flags Detected")
                            st.error(red_flags)
                        
                        # Recommendation
                        if recommendation:
                            st.markdown("### Recommendation")
                            st.info(recommendation)
                        
                        # Full AI response
                        with st.expander("View Full AI Analysis"):
                            st.text(result_text)
                        
                        # Disclaimer
                        st.divider()
                        st.caption("""
                        **Disclaimer:** This analysis is AI-generated and should be used as guidance only. 
                        Always verify important information through multiple credible sources and apply critical thinking.
                        """)
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
            else:
                st.warning("Please enter or upload article text to analyze.")

# Tab 6: About Website Model
with tab6:
    st.markdown("### Website Credibility Model")
    st.divider()
    
    st.markdown("""
    ### Overview
    
    This application uses machine learning to assess the credibility and trustworthiness of websites
    based on various metadata features including security, infrastructure, and transparency indicators.
    
    ### Model Performance
    
    - **Accuracy:** 85.00% - Correctly classifies 85% of websites
    - **F1-Score:** 0.8370 - Excellent balance between precision and recall
    - **Model Type:** Extra Trees Classifier
    - **Features:** 67 engineered features (from 24 base features with one-hot encoding)
    
    ### Key Features Analyzed
    
    **1. Security Indicators**
    - HTTPS/SSL certificate validity
    - TLS version and certificate type
    - SSL issuer reputation
    
    **2. Domain Characteristics**
    - Domain age and registrar
    - WHOIS privacy settings
    
    **3. Performance Metrics**
    - Page load time
    - Redirect behavior
    - Server response codes
    
    **4. Content Quality**
    - Advertisement density
    - External links
    - Popup presence
    
    **5. Infrastructure**
    - Server location
    - Hosting type
    - CDN usage
    
    **6. Transparency**
    - Contact information availability
    - Privacy policy and terms of service
    - Social media presence
    
    ### Important Notes
    
    - This tool provides an automated assessment based on metadata features
    - Results should be used as one factor in evaluating website trustworthiness
    - The model was trained on a balanced dataset including edge cases
    - Always exercise caution and use multiple verification methods
    
    ### Version Information
    
    - **Training Date:** February 8, 2026
    - **NumPy Version:** 1.26.4
    - **Scikit-learn Version:** 1.8.0
    - **Model Version:** 1.0
    
    ---
    
    Developed for website credibility classification using advanced machine learning techniques.
    """)

# Tab 7: Documentation
with tab7:
    st.markdown("### Documentation & Model Information")
    st.divider()
    
    # Fake News Detection Section
    st.markdown("### 1. Fake News Detection (Gemini AI)")
    st.markdown("""
    #### Overview
    
    The Fake News Detection feature uses Google's **Gemini 2.0 Flash Lite** AI model to analyze news articles 
    and text content for signs of misinformation, bias, and unreliable information.
    
    #### How It Works
    
    **Advanced AI Analysis:**
    - Evaluates factual accuracy and verifiability
    - Identifies emotional manipulation and sensationalism
    - Assesses logical consistency and reasoning
    - Examines use of credible citations
    - Detects bias, propaganda, or misleading framing
    - Analyzes writing quality and professionalism
    
    **Key Benefits:**
    - 🚀 **No Large Downloads:** API-based, no 1.2GB model files
    - ⚡ **Fast & Accurate:** State-of-the-art Gemini AI
    - 💡 **Detailed Explanations:** AI provides reasoning for verdicts
    - 🔍 **Red Flag Detection:** Identifies specific concerning elements
    - 📊 **Confidence Scoring:** Get percentage confidence in assessments
    
    #### Setup Instructions
    
    1. **Get Your Free API Key:**
       - Visit: https://makersuite.google.com/app/apikey
       - Sign in with your Google account
       - Click "Create API Key"
       - Copy the key
    
    2. **Configure in App:**
       - Enter your API key in the sidebar
       - Look for "Gemini API Key" input field
       - The key is securely stored in your session
    
    3. **Start Analyzing:**
       - Navigate to the "News Analysis" tab
       - Paste article text or upload a .txt file
       - Click "Analyze Article"
    
    #### Output Format
    
    The analysis provides:
    - **Verdict:** LEGITIMATE, FAKE, or MISLEADING
    - **Confidence Level:** Percentage score with progress bar
    - **AI Reasoning:** 2-3 sentence explanation
    - **Red Flags:** Specific concerning elements detected
    - **Recommendation:** Actionable advice for users
    - **Full Analysis:** Complete AI response available in expander
    
    #### Best Practices
    
    - Analyze complete articles for best results
    - Use for guidance, not as sole fact-checking source
    - Verify important claims through multiple sources
    - Consider context and source reputation
    - Longer articles (100+ words) yield better analysis
    
    
    ---
    
    ### 2. Website Credibility Model
    
    #### Overview
    
    The Website Credibility feature uses a machine learning stacking ensemble to assess the trustworthiness
    of websites based on 67 engineered features extracted from domain metadata, security indicators,
    and infrastructure characteristics.
    
    #### Model Performance
    
    - **Accuracy:** 85.00%
    - **F1-Score:** 0.8370
    - **Model Type:** Extra Trees Classifier (Stacking Ensemble)
    - **Features:** 67 total (24 base features + one-hot encoding)
    
    #### Key Features Analyzed
    
    **Security Indicators:**
    - HTTPS/SSL certificate validity
    - TLS version and certificate type
    - SSL issuer reputation
    
    **Domain Characteristics:**
    - Domain age and registrar
    - WHOIS privacy settings
    
    **Performance Metrics:**
    - Page load time
    - Redirect count
    - Server response codes
    
    **Content & Trust Signals:**
    - Ads density score
    - External links count
    - Contact information availability
    - Privacy policy presence
    - Mobile responsiveness
    
    #### Usage
    
    1. Enter website URL in "URL Analysis" tab
    2. Click "Analyze Website"
    3. View extracted metadata and credibility score
    
    ---
    
    ### 3. AI Image Detection Model
    """)
    
    st.divider()
    
    st.markdown("""
    ### Overview
    
    This module analyzes images to determine whether they were generated by artificial intelligence
    or are authentic photographs taken with real cameras.
    
    ### How It Works
    
    The model examines various aspects of an image:
    
    **1. Visual Pattern Analysis**
    - Detects synthetic patterns common in AI-generated images
    - Identifies unnatural regularities in texture and structure
    
    **2. Artifact Detection**
    - Looks for telltale signs of AI generation
    - Examines edge consistency and noise patterns
    
    **3. Statistical Analysis**
    - Analyzes color distribution
    - Examines frequency domain characteristics
    - Detects anomalies in pixel relationships
    
    **4. Metadata Examination**
    - Checks for camera information
    - Verifies file properties
    - Examines EXIF data when available
    
    ### Use Cases
    
    - **Content Verification:** Verify the authenticity of images for journalism and research
    - **Social Media:** Identify potentially misleading AI-generated content
    - **Digital Forensics:** Support investigations requiring image authenticity verification
    - **Content Moderation:** Assist in identifying synthetic media
    
    ### Important Considerations
    
    - **Not 100% Accurate:** No AI detection system is perfect
    - **Evolving Technology:** AI generation techniques constantly improve
    - **Context Matters:** Use results as one factor in overall assessment
    - **Multiple Checks:** Combine with other verification methods
    - **False Positives:** Heavily edited real photos may be flagged
    - **False Negatives:** Very sophisticated AI images may pass undetected
    
    ### Best Practices
    
    1. Use high-quality, uncompressed images when possible
    2. Consider the source and context of the image
    3. Look for additional verification from multiple tools
    4. Be aware that compression can affect results
    5. Understand that professional photo editing may trigger false positives
    
    ### Model Status
    
    """)
    
    if image_model_loaded:
        st.success("""
        **Status: Active**
        
        The AI image detection model is loaded and ready for analysis.
        Upload images in the Image Detection tab to begin analysis.
        """)
    else:
        st.warning("""
        **Status: Not Available**
        
        The AI image detection model is not currently loaded.
        To enable this feature, add the model file to the project directory.
        """)
    
    st.markdown("""
    
    #### Technical Notes
    
    The image preprocessing pipeline may require adjustment based on the specific model used.
    Common requirements include:
    - Specific image dimensions (e.g., 224x224, 256x256)
    - Normalization ranges (0-1 or -1 to 1)
    - Color space (RGB, BGR, grayscale)
    - Input tensor shape
    
    If you encounter errors, verify that the preprocessing matches your model's training configuration.
    
    ---
    
    **AI Image Detection: Powered by Machine Learning**
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p style='margin: 0;'>AI Detection Suite v2.0</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Professional Multi-Model Analysis Platform for Content Verification and Authenticity Detection</p>
</div>
""", unsafe_allow_html=True)
