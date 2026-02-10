"""
Test what the model considers TRUSTED
"""
import pandas as pd
import joblib

# Load model
model = joblib.load('stacking_model.joblib')
features = joblib.load('feature_names.joblib')[:model.n_features_in_]

print("TESTING: What does model consider TRUSTED?\n")

# Test 1: Perfect trusted site
print("=" * 80)
print("TEST 1: PERFECT TRUSTED SITE")
print("=" * 80)

perfect_trusted = {
    'has_https': 'Yes',
    'ssl_valid': 'Yes',
    'ssl_issuer': 'DigiCert',
    'tls_version': 'TLS 1.3',
    'certificate_type': 'EV',
    'domain_age_years': 20.0,
    'domain_registrar': 'MarkMonitor',
    'whois_privacy_enabled': False,
    'page_load_time_sec': 1.0,
    'redirect_count': 0,
    'server_response_code': 200,
    'ads_density_score': 0.0,
    'external_links_count': 10,
    'server_location': 'USA',
    'hosting_type': 'dedicated',
    'contact_info_available': True,
    'privacy_policy_exists': True,
    'terms_of_service_exists': True,
    'social_media_presence': 'medium',
    'content_update_frequency': 'hourly',
    'mobile_responsive': 'Yes'
}

df1 = pd.DataFrame([perfect_trusted])
df1_enc = pd.get_dummies(df1)
df1_final = pd.DataFrame(0, index=[0], columns=features)
for col in df1_enc.columns:
    if col in features:
        df1_final[col] = df1_enc[col].values[0]

pred1 = model.predict(df1_final)[0]
prob1 = model.predict_proba(df1_final)[0]

print(f"Result: {'TRUSTED' if pred1 == 1 else 'UNTRUSTED'}")
print(f"Confidence: {max(prob1)*100:.1f}%")
print(f"Probabilities: Untrusted={prob1[0]*100:.1f}%, Trusted={prob1[1]*100:.1f}%\n")

# Test 2: What GitHub actually has
print("=" * 80)
print("TEST 2: GITHUB VALUES WITH BETTER REGISTRAR")
print("=" * 80)

github_improved = {
    'has_https': 'Yes',
    'ssl_valid': 'Yes',
    'ssl_issuer': 'DigiCert',  # Changed from Comodo
    'tls_version': 'TLS 1.3',
    'certificate_type': 'EV',  # Changed from DV
    'domain_age_years': 18.3,
    'domain_registrar': 'MarkMonitor',  # Changed from Unknown
    'whois_privacy_enabled': False,
    'page_load_time_sec': 0.33,
    'redirect_count': 0,
    'server_response_code': 200,
    'ads_density_score': 0.07,
    'external_links_count': 12,
    'server_location': 'USA',  # Changed from Unknown
    'hosting_type': 'dedicated',  # Changed from empty
    'contact_info_available': True,
    'privacy_policy_exists': True,
    'terms_of_service_exists': True,
    'social_media_presence': 'medium',
    'content_update_frequency': 'hourly',  # Changed from irregular
    'mobile_responsive': 'Yes'
}

df2 = pd.DataFrame([github_improved])
df2_enc = pd.get_dummies(df2)
df2_final = pd.DataFrame(0, index=[0], columns=features)
for col in df2_enc.columns:
    if col in features:
        df2_final[col] = df2_enc[col].values[0]

pred2 = model.predict(df2_final)[0]
prob2 = model.predict_proba(df2_final)[0]

print(f"Result: {'TRUSTED' if pred2 == 1 else 'UNTRUSTED'}")
print(f"Confidence: {max(prob2)*100:.1f}%")
print(f"Probabilities: Untrusted={prob2[0]*100:.1f}%, Trusted={prob2[1]*100:.1f}%\n")

# Test 3: Minimal trusted
print("=" * 80)
print("TEST 3: MINIMAL EXAMPLE FROM TRAINING DATA")
print("=" * 80)

# Load one of the trusted sources
import pandas as pd
trusted_df = pd.read_csv('trusted_sources_original.csv')
if len(trusted_df) > 0:
    print(f"Sample trusted site from training:</n{trusted_df.iloc[0].to_dict()}\n")
    
    sample = trusted_df.iloc[0].to_dict()
    df3 = pd.DataFrame([sample])
    df3_enc = pd.get_dummies(df3)
    df3_final = pd.DataFrame(0, index=[0], columns=features)
    for col in df3_enc.columns:
        if col in features:
            df3_final[col] = df3_enc[col].values[0]
    
    pred3 = model.predict(df3_final)[0]
    prob3 = model.predict_proba(df3_final)[0]
    
    print(f"Result: {'TRUSTED' if pred3 == 1 else 'UNTRUSTED'}")
    print(f"Confidence: {max(prob3)*100:.1f}%")
    print(f"Probabilities: Untrusted={prob3[0]*100:.1f}%, Trusted={prob3[1]*100:.1f}%")
