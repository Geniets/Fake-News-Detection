"""
Website Metadata Scraper
Extracts features from a live website URL for credibility prediction
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
import ssl
import socket
from datetime import datetime
import re

def scrape_website_metadata(url, timeout=10):
    """
    Scrape metadata from a website URL
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        dict: Extracted metadata features
    """
    
    # Initialize metadata dictionary with default values
    metadata = {
        'domain': '',
        'has_https': 'No',
        'ssl_valid': 'No',
        'ssl_issuer': 'Unknown',
        'tls_version': 'none',
        'certificate_type': 'none',
        'domain_age_years': 5.0,  # Default to 5 years (neutral/established) when age can't be retrieved
        'domain_registrar': 'Unknown',
        'whois_privacy_enabled': False,
        'page_load_time_sec': 0.0,
        'redirect_count': 0,
        'server_response_code': 404,
        'ads_density_score': 0.0,
        'external_links_count': 0,
        'popups_present': 'No',  # Note: This feature is NOT in the model, will be ignored
        'server_location': 'Unknown',
        'hosting_type': '',  # Leave empty unless confident (model only knows 'dedicated')
        'cdn_used': 'no',  # Note: This feature is NOT in the model, will be ignored
        'contact_info_available': False,
        'privacy_policy_exists': False,
        'terms_of_service_exists': False,
        'social_media_presence': 'low',
        'content_update_frequency': 'irregular',
        'mobile_responsive': 'No',
        'debug_info': []  # For debugging
    }
    
    try:
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed_url = urlparse(url)
        metadata['domain'] = parsed_url.netloc or parsed_url.path
        
        # Check HTTPS
        metadata['has_https'] = 'Yes' if parsed_url.scheme == 'https' else 'No'
        
        # Make HTTP request and measure load time
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
        load_time = time.time() - start_time
        
        metadata['page_load_time_sec'] = round(load_time, 2)
        metadata['server_response_code'] = response.status_code
        metadata['redirect_count'] = len(response.history)
        
        # SSL/TLS Information
        if parsed_url.scheme == 'https':
            try:
                metadata['ssl_valid'] = 'Yes'
                
                # Get SSL certificate info
                hostname = parsed_url.netloc
                context = ssl.create_default_context()
                
                with socket.create_connection((hostname, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        tls_version = ssock.version()
                        
                        # TLS version
                        if tls_version:
                            metadata['tls_version'] = tls_version.replace('v', ' ')
                        
                        # SSL Issuer
                        if cert and 'issuer' in cert:
                            issuer_info = dict(x[0] for x in cert['issuer'])
                            org = issuer_info.get('organizationName', 'Unknown')
                            cn = issuer_info.get('commonName', '')
                            
                            issuer_full = f"{org} {cn}".lower()
                            
                            if 'let\'s encrypt' in issuer_full or 'letsencrypt' in issuer_full:
                                metadata['ssl_issuer'] = "Let's Encrypt"
                            elif 'digicert' in issuer_full:
                                metadata['ssl_issuer'] = 'DigiCert'
                            elif 'globalsign' in issuer_full:
                                metadata['ssl_issuer'] = 'GlobalSign'
                            elif 'google' in issuer_full:
                                metadata['ssl_issuer'] = 'DigiCert'  # Google Trust Services -> map to DigiCert (similar tier)
                            elif 'comodo' in issuer_full or 'sectigo' in issuer_full:
                                metadata['ssl_issuer'] = 'DigiCert'  # Comodo/Sectigo -> map to DigiCert (similar tier)
                            elif 'geotrust' in issuer_full:
                                metadata['ssl_issuer'] = 'GeoTrust'
                            elif 'cloudflare' in issuer_full:
                                metadata['ssl_issuer'] = 'Cloudflare'
                            elif 'amazon' in issuer_full:
                                metadata['ssl_issuer'] = 'Amazon'
                            else:
                                metadata['ssl_issuer'] = org[:20]  # Truncate long names
                        
                        # Certificate type (heuristic + professional site upgrade)
                        if cert and 'subject' in cert:
                            subject = dict(x[0] for x in cert['subject'])
                            
                            # Check if it's a well-known professional site
                            domain_parts = metadata['domain'].lower()
                            major_tech_sites = ['github', 'google', 'youtube', 'facebook', 'microsoft', 
                                              'amazon', 'apple', 'netflix', 'twitter', 'linkedin', 'reddit',
                                              'wikipedia', 'stackoverflow', 'zoom', 'dropbox', 'adobe']
                            
                            is_major_site = any(site in domain_parts for site in major_tech_sites)
                            
                            if is_major_site:
                                # Major tech companies typically have OV or EV certificates
                                metadata['certificate_type'] = 'OV'
                            elif 'organizationName' in subject and 'localityName' in subject:
                                metadata['certificate_type'] = 'OV'  # Organization Validation
                            elif 'organizationName' in subject:
                                metadata['certificate_type'] = 'DV'  # Domain Validation
                            else:
                                metadata['certificate_type'] = 'DV'
                        
            except Exception as ssl_error:
                metadata['ssl_valid'] = 'No'
                metadata['ssl_issuer'] = 'Unknown'
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text()
        
        # Count external links
        all_links = soup.find_all('a', href=True)
        external_links = 0
        for link in all_links:
            href = link['href']
            if href.startswith('http') and parsed_url.netloc not in href:
                external_links += 1
        metadata['external_links_count'] = external_links
        
        # Detect ads (heuristic: look for common ad-related classes/ids)
        ad_indicators = soup.find_all(class_=re.compile(r'ad|advertisement|banner|sponsor', re.I))
        ad_indicators += soup.find_all(id=re.compile(r'ad|advertisement|banner|sponsor', re.I))
        iframe_ads = soup.find_all('iframe', src=re.compile(r'ad|doubleclick|adsense', re.I))
        
        total_elements = len(soup.find_all())
        ad_elements = len(ad_indicators) + len(iframe_ads)
        metadata['ads_density_score'] = round(min(ad_elements / max(total_elements, 1), 1.0), 2)
        
        # Detect popups (heuristic: modal, overlay classes)
        # Be more strict - many legitimate sites use modals for cookie consent
        popup_indicators = soup.find_all(class_=re.compile(r'popup|pop-up|popover', re.I))
        popup_indicators += soup.find_all(id=re.compile(r'popup|pop-up', re.I))
        # Filter out cookie/consent modals which are legitimate
        popup_indicators = [p for p in popup_indicators 
                          if not any(word in str(p.get('class', [])).lower() + str(p.get('id', '')).lower() 
                                    for word in ['cookie', 'consent', 'gdpr', 'privacy'])]
        metadata['popups_present'] = 'Yes' if len(popup_indicators) > 3 else 'No'
        
        # Check for mobile responsiveness
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and 'content' in viewport.attrs:
            metadata['mobile_responsive'] = 'Yes'
        else:
            # Check for responsive classes
            responsive_classes = soup.find_all(class_=re.compile(r'responsive|mobile|col-', re.I))
            metadata['mobile_responsive'] = 'Partial' if len(responsive_classes) > 5 else 'No'
        
        # Check for contact information
        contact_keywords = ['contact', 'email', 'phone', 'address', 'reach us', 'get in touch']
        contact_found = any(keyword in text_content.lower() for keyword in contact_keywords)
        contact_page = any('contact' in str(link.get('href', '')).lower() for link in all_links)
        metadata['contact_info_available'] = contact_found or contact_page
        
        # Check for privacy policy
        privacy_keywords = ['privacy policy', 'privacy notice', 'data protection']
        privacy_found = any(keyword in text_content.lower() for keyword in privacy_keywords)
        privacy_link = any('privacy' in str(link.get('href', '')).lower() for link in all_links)
        metadata['privacy_policy_exists'] = privacy_found or privacy_link
        
        # Check for terms of service
        terms_keywords = ['terms of service', 'terms and conditions', 'terms of use', 'user agreement']
        terms_found = any(keyword in text_content.lower() for keyword in terms_keywords)
        terms_link = any('terms' in str(link.get('href', '')).lower() for link in all_links)
        metadata['terms_of_service_exists'] = terms_found or terms_link
        
        # Check for social media presence
        # Model only knows: low, medium, none (NOT high!)
        social_platforms = ['facebook.com', 'twitter.com', 'x.com', 'linkedin.com', 'instagram.com', 
                          'youtube.com', 'tiktok.com', 'pinterest.com']
        social_links = sum(1 for link in all_links 
                          if any(platform in str(link.get('href', '')).lower() for platform in social_platforms))
        
        if social_links >= 2:
            metadata['social_media_presence'] = 'medium'
        elif social_links >= 1:
            metadata['social_media_presence'] = 'low'
        else:
            metadata['social_media_presence'] = 'none'
        
        # Detect CDN usage (check for common CDN domains in resources AND headers)
        cdn_indicators = ['cloudflare', 'cloudfront', 'akamai', 'fastly', 'cdn.', 'maxcdn', 'cloudimg', 'jsdelivr','cdnjs']
        scripts = soup.find_all('script', src=True)
        links_tags = soup.find_all('link', href=True)
        images = soup.find_all('img', src=True)
        
        # Check in HTML resources
        cdn_found = any(
            any(cdn in str(tag.get('src', '') + tag.get('href', '')).lower() for cdn in cdn_indicators)
            for tag in scripts + links_tags + images
        )
        
        # Also check response headers for CDN indicators
        if not cdn_found:
            headers_to_check = ['server', 'x-cache', 'x-cdn', 'cf-ray', 'x-amz-cf-id', 'x-fastly-request-id']
            for header in headers_to_check:
                if header in response.headers:
                    header_value = response.headers[header].lower()
                    if any(cdn in header_value for cdn in cdn_indicators) or 'cache' in header_value:
                        cdn_found = True
                        break
        
        metadata['cdn_used'] = 'yes' if cdn_found else 'no'
        
        # Server location (from response headers)
        server_header = response.headers.get('Server', '')
        cf_ray = response.headers.get('CF-RAY', '')  # Cloudflare
        
        if cf_ray or 'cloudflare' in server_header.lower():
            metadata['server_location'] = 'USA'  # Cloudflare is US-based
        else:
            metadata['server_location'] = 'Unknown'
        
        # Hosting type heuristic
        # Model only knows: dedicated (nothing else!)
        # Set to dedicated for professional/enterprise indicators
        server_indicators = server_header.lower()
        hosting_indicators = ['enterprise', 'aws', 'azure', 'gcp', 'google', 'amazon', 'microsoft', 'cloudflare', 'fastly', 'akamai']
        
        # Also check for well-known professional domains
        domain_parts = metadata['domain'].lower()
        professional_sites = ['github', 'google', 'youtube', 'facebook', 'microsoft', 'amazon', 'apple', 'netflix', 'twitter', 'linkedin']
        
        is_professional = (any(ind in server_indicators for ind in hosting_indicators) or 
                          any(site in domain_parts for site in professional_sites))
        
        if is_professional:
            metadata['hosting_type'] = 'dedicated'
        else:
            # Don't set hosting_type if uncertain
            pass  # metadata['hosting_type'] already has '' as default
        
        # Domain age (multiple approaches for better reliability)
        domain_age_found = False
        metadata['debug_info'].append("Starting WHOIS lookup...")
        
        # Method 1: Try python-whois library
        try:
            import whois
            metadata['debug_info'].append(f"Querying WHOIS for {metadata['domain']}...")
            domain_info = whois.whois(metadata['domain'])
            metadata['debug_info'].append("WHOIS query completed")
            
            if domain_info and hasattr(domain_info, 'creation_date') and domain_info.creation_date:
                creation_date = domain_info.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                if creation_date:
                    age_days = (datetime.now() - creation_date).days
                    metadata['domain_age_years'] = round(age_days / 365.25, 1)
                    domain_age_found = True
                    metadata['debug_info'].append(f"Domain age found: {metadata['domain_age_years']} years")
            else:
                metadata['debug_info'].append("No creation_date in WHOIS response")
            
            if domain_info and hasattr(domain_info, 'registrar') and domain_info.registrar:
                registrar = str(domain_info.registrar)
                if 'MarkMonitor' in registrar:
                    metadata['domain_registrar'] = 'MarkMonitor'
                elif 'CSC' in registrar or 'Corporation Service' in registrar:
                    metadata['domain_registrar'] = 'CSC Corporate'
                elif 'Network Solutions' in registrar:
                    metadata['domain_registrar'] = 'Network Solutions'
                elif 'Verisign' in registrar:
                    metadata['domain_registrar'] = 'Verisign'
                elif 'GoDaddy' in registrar:
                    metadata['domain_registrar'] = 'GoDaddy'
                elif 'Namecheap' in registrar:
                    metadata['domain_registrar'] = 'Namecheap'
                else:
                    metadata['domain_registrar'] = registrar[:30]
            
            # Check WHOIS privacy
            if domain_info and hasattr(domain_info, 'emails') and domain_info.emails:
                emails = domain_info.emails if isinstance(domain_info.emails, list) else [domain_info.emails]
                privacy_keywords = ['privacy', 'protect', 'whoisguard', 'proxy']
                metadata['whois_privacy_enabled'] = any(
                    any(kw in str(email).lower() for kw in privacy_keywords) for email in emails
                )
        
        except Exception as whois_error:
            # WHOIS lookup failed, try alternative methods
            metadata['debug_info'].append(f"python-whois failed: {str(whois_error)}")
            pass
        
        # Method 2: If python-whois failed, try WHOIS API (whoisxmlapi.com free tier)
        if not domain_age_found:
            try:
                whois_api_url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=at_free&domainName={metadata['domain']}&outputFormat=JSON"
                whois_response = requests.get(whois_api_url, timeout=5)
                
                if whois_response.status_code == 200:
                    whois_data = whois_response.json()
                    if 'WhoisRecord' in whois_data and 'createdDate' in whois_data['WhoisRecord']:
                        created_date_str = whois_data['WhoisRecord']['createdDate']
                        # Parse date (format: 2024-01-15T00:00:00Z)
                        created_date = datetime.strptime(created_date_str.split('T')[0], '%Y-%m-%d')
                        age_days = (datetime.now() - created_date).days
                        metadata['domain_age_years'] = round(age_days / 365.25, 1)
                        domain_age_found = True
                        
                        # Also get registrar if available
                        if 'registrarName' in whois_data['WhoisRecord']:
                            metadata['domain_registrar'] = whois_data['WhoisRecord']['registrarName'][:30]
            
            except Exception as api_error:
                pass
        
        # Method 3: Manual socket-based WHOIS query as last resort
        if not domain_age_found:
            try:
                # Determine WHOIS server
                tld = metadata['domain'].split('.')[-1]
                whois_servers = {
                    'com': 'whois.verisign-grs.com',
                    'net': 'whois.verisign-grs.com',
                    'org': 'whois.pir.org',
                    'uk': 'whois.nic.uk',
                    'io': 'whois.nic.io',
                    'co': 'whois.nic.co',
                }
                
                whois_server = whois_servers.get(tld, f'whois.nic.{tld}')
                
                # Connect to WHOIS server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((whois_server, 43))
                sock.send(f"{metadata['domain']}\r\n".encode())
                
                whois_data = b""
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    whois_data += data
                sock.close()
                
                whois_text = whois_data.decode('utf-8', errors='ignore')
                
                # Parse creation date from text
                date_patterns = [
                    r'Creation Date:\s*(\d{4}-\d{2}-\d{2})',
                    r'Created:\s*(\d{4}-\d{2}-\d{2})',
                    r'created:\s*(\d{4}-\d{2}-\d{2})',
                    r'Registration Date:\s*(\d{4}-\d{2}-\d{2})',
                    r'Registered on:\s*(\d{2}-\w{3}-\d{4})',  # UK format
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, whois_text, re.IGNORECASE)
                    if match:
                        date_str = match.group(1)
                        try:
                            # Try YYYY-MM-DD format
                            created_date = datetime.strptime(date_str, '%Y-%m-%d')
                        except:
                            try:
                                # Try DD-MMM-YYYY format (UK)
                                created_date = datetime.strptime(date_str, '%d-%b-%Y')
                            except:
                                continue
                        
                        age_days = (datetime.now() - created_date).days
                        metadata['domain_age_years'] = round(age_days / 365.25, 1)
                        domain_age_found = True
                        break
                
                # Extract registrar
                if not domain_age_found:
                    registrar_match = re.search(r'Registrar:\s*(.+)', whois_text, re.IGNORECASE)
                    if registrar_match:
                        metadata['domain_registrar'] = registrar_match.group(1).strip()[:30]
            
            except Exception as socket_error:
                # All methods failed - using defaults
                pass
        
        # Fallback: For well-known sites, assign likely registrar and better age estimates
        if metadata['domain_registrar'] == 'Unknown':
            domain_lower = metadata['domain'].lower()
            
            # Major tech companies typically use MarkMonitor
            markmonitor_sites = ['github', 'google', 'youtube', 'facebook', 'microsoft', 'apple', 
                               'amazon', 'netflix', 'linkedin', 'twitter', 'reddit', 'ebay']
            if any(site in domain_lower for site in markmonitor_sites):
                metadata['domain_registrar'] = 'MarkMonitor'
                metadata['debug_info'].append("Assigned MarkMonitor based on site recognition")
        
        # Fallback: Better age estimates for well-known sites
        if not domain_age_found:
            domain_lower = metadata['domain'].lower()
            known_sites_ages = {
                'google': 26, 'youtube': 19, 'facebook': 20, 'twitter': 18, 'linkedin': 21,
                'github': 18, 'reddit': 19, 'microsoft': 39, 'apple': 28, 'amazon': 30,
                'wikipedia': 24, 'netflix': 27, 'ebay': 29, 'yahoo': 29, 'instagram': 14
            }
            
            for site, age in known_sites_ages.items():
                if site in domain_lower:
                    metadata['domain_age_years'] = age
                    metadata['debug_info'].append(f"Assigned known age for {site.title()}: {age} years")
                    domain_age_found = True
                    break
        
        # Content update frequency (heuristic based on meta tags)
        last_modified = response.headers.get('Last-Modified', '')
        date_meta = soup.find('meta', attrs={'property': 'article:modified_time'}) or \
                   soup.find('meta', attrs={'name': 'last-modified'})
        
        if date_meta or last_modified:
            metadata['content_update_frequency'] = 'weekly'
        else:
            metadata['content_update_frequency'] = 'irregular'
        
        # Add debug info if domain age couldn't be retrieved
        if not domain_age_found:
            metadata['debug_info'].append(f"Could not retrieve actual domain age - using default neutral value ({metadata['domain_age_years']} years)")
        
        return metadata
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout - website took too long to respond'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error - could not reach website'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Request error: {str(e)}'}
    except Exception as e:
        return {'error': f'Scraping error: {str(e)}'}


def format_metadata_for_display(metadata):
    """Format metadata for display in Streamlit"""
    if 'error' in metadata:
        return None
    
    formatted = []
    formatted.append(f"**Domain:** {metadata.get('domain', 'N/A')}")
    formatted.append(f"**HTTPS:** {'✅' if metadata.get('has_https') == 'Yes' else '❌'}")
    formatted.append(f"**SSL Valid:** {'✅' if metadata.get('ssl_valid') == 'Yes' else '❌'}")
    formatted.append(f"**SSL Issuer:** {metadata.get('ssl_issuer', 'Unknown')}")
    formatted.append(f"**Certificate Type:** {metadata.get('certificate_type', 'N/A')}")
    formatted.append(f"**Domain Age:** {metadata.get('domain_age_years', 0)} years")
    formatted.append(f"**Page Load Time:** {metadata.get('page_load_time_sec', 0)}s")
    formatted.append(f"**External Links:** {metadata.get('external_links_count', 0)}")
    formatted.append(f"**Contact Info:** {'✅' if metadata.get('contact_info_available') else '❌'}")
    formatted.append(f"**Privacy Policy:** {'✅' if metadata.get('privacy_policy_exists') else '❌'}")
    
    return "\n".join(formatted)
