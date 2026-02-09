import pandas as pd
import joblib

# Load training data
metadata = pd.read_csv('website_metadata_examples.csv')
trusted_sources = pd.read_csv('trusted_sources_original.csv')
trusted_labeled = trusted_sources[['domain']].copy()
trusted_labeled['credibility_label'] = 1

df = metadata.merge(trusted_labeled, on='domain', how='inner')

print("=" * 80)
print("COMPARING GITHUB TO TRUSTED SITES IN TRAINING DATA")
print("=" * 80)

# Get average/common values for trusted sites
print("\n📊 TRUSTED SITES STATISTICS:")
print(f"Total trusted sites: {len(df)}")

print("\n🔒 SECURITY FEATURES (Trusted Sites):")
print(f"  HTTPS: {(df['has_https']==True).sum()/len(df)*100:.1f}% have HTTPS")
print(f"  Valid SSL: {(df['ssl_valid']==True).sum()/len(df)*100:.1f}% have valid SSL")
print(f"  SSL Issuers: {df['ssl_issuer'].value_counts().head(5).to_dict()}")
print(f"  Cert Types: {df['certificate_type'].value_counts().to_dict()}")
print(f"  TLS Versions: {df['tls_version'].value_counts().to_dict()}")

print("\n🌐 DOMAIN FEATURES:")
print(f"  Avg Domain Age: {df['domain_age_years'].mean():.1f} years")
print(f"  Registrars: {df['domain_registrar'].value_counts().head(5).to_dict()}")
print(f"  WHOIS Privacy: {(df['whois_privacy_enabled']==True).sum()/len(df)*100:.1f}%")

print("\n🏢 INFRASTRUCTURE:")
print(f"  Hosting Types: {df['hosting_type'].value_counts().to_dict()}")
print(f"  CDN Usage: {df['cdn_used'].value_counts().to_dict()}")
print(f"  Server Locations: {df['server_location'].value_counts().head().to_dict()}")

print("\n📄 TRUST INDICATORS:")
print(f"  Contact Info: {(df['contact_info_available']==True).sum()/len(df)*100:.1f}%")
print(f"  Privacy Policy: {(df['privacy_policy_exists']==True).sum()/len(df)*100:.1f}%")
print(f"  Terms of Service: {(df['terms_of_service_exists']==True).sum()/len(df)*100:.1f}%")
print(f"  Social Media: {df['social_media_presence'].value_counts().to_dict()}")
print(f"  Mobile Responsive: {(df['mobile_responsive']==True).sum()/len(df)*100:.1f}%")

print("\n📈 CONTENT QUALITY:")
print(f"  Avg Ads Density: {df['ads_density_score'].mean():.3f}")
print(f"  Popups: {df['popups_present'].value_counts().to_dict()}")
print(f"  Content Update: {df['content_update_frequency'].value_counts().to_dict()}")

print("\n" + "=" * 80)
print("GITHUB'S VALUES VS TRUSTED AVERAGE:")
print("=" * 80)

github_values = {
    'ssl_issuer': 'Comodo',
    'certificate_type': 'DV',
    'domain_age_years': 18.3,
    'domain_registrar': 'Unknown',
    'hosting_type': '',
    'cdn_used': 'no',
    'popups_present': 'yes',
    'ads_density_score': 0.07
}

print("\n⚠️ MISMATCHES:")
if github_values['domain_registrar'] == 'Unknown':
    print("  ❌ Registrar: Unknown (most trusted sites have named registrars)")
if github_values['certificate_type'] == 'DV':
    trusted_dv = (df['certificate_type']=='DV').sum()
    print(f"  ⚠️ Cert Type: DV (only {trusted_dv}/{len(df)} trusted sites use DV)")
if github_values['cdn_used'] == 'no':
    trusted_cdn = (df['cdn_used']=='yes').sum()
    print(f"  ❌ CDN: Not detected (but {trusted_cdn}/{len(df)} trusted sites use CDN)")
if github_values['hosting_type'] == '':
    print(f"  ⚠️ Hosting: Empty (trusted sites typically show hosting type)")
if github_values['popups_present'] == 'yes':
    trusted_popups = (df['popups_present']=='yes').sum()
    print(f"  ❌ Popups: Detected (only {trusted_popups}/{len(df)} trusted sites have popups)")

print("\n✅ MATCHES:")
print(f"  Domain Age: {github_values['domain_age_years']} years (avg trusted: {df['domain_age_years'].mean():.1f} years)")
print(f"  Ads Density: {github_values['ads_density_score']:.2f} (avg trusted: {df['ads_density_score'].mean():.3f})")
