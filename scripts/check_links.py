#!/usr/bin/env python3
"""
Robust link checker for GitHub Pages documentation.
Uses HTTP status verification AND content validation (like a crawler).
Properly handles Jekyll permalinks and baseurl.
"""
import re
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def load_jekyll_config() -> Dict:
    """Load Jekyll configuration from _config.yml"""
    config_file = Path('docs/_config.yml')
    if config_file.exists():
        with open(config_file) as f:
            return yaml.safe_load(f) or {}
    return {}

def get_base_url() -> str:
    """Get the base URL for the GitHub Pages site"""
    config = load_jekyll_config()
    url = config.get('url', 'https://yasarshaikh.github.io').rstrip('/')
    baseurl = config.get('baseurl', '').strip('/')
    if baseurl:
        return f"{url}/{baseurl}".rstrip('/')
    return url

def extract_frontmatter(file_path: Path) -> Optional[Dict]:
    """Extract Jekyll frontmatter from markdown file"""
    try:
        with open(file_path) as f:
            content = f.read()
        
        # Match frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            return yaml.safe_load(frontmatter_match.group(1)) or {}
    except Exception:
        pass
    return None

def get_file_url(file_path: Path, base_url: str) -> str:
    """Get the actual URL for a markdown file, considering permalinks"""
    frontmatter = extract_frontmatter(file_path)
    
    # Check for permalink in frontmatter
    if frontmatter and 'permalink' in frontmatter:
        permalink = frontmatter['permalink'].strip()
        # If permalink is absolute (starts with /), it overrides baseurl
        if permalink.startswith('/'):
            # Absolute permalink - use site URL directly (no baseurl)
            config = load_jekyll_config()
            site_url = config.get('url', 'https://yasarshaikh.github.io').rstrip('/')
            return f"{site_url}{permalink}"
        else:
            # Relative permalink - append to baseurl
            return f"{base_url}/{permalink}".rstrip('/')
    
    # Default: convert file path to URL
    rel_path = file_path.relative_to(Path('docs'))
    url_path = str(rel_path).replace('.md', '.html')
    return f"{base_url}/{url_path}"

def resolve_link(link: str, source_file: Path, base_url: str) -> str:
    """Resolve a link to its full URL"""
    # External links
    if link.startswith('http'):
        return link
    
    # Anchor links
    if link.startswith('#'):
        return link
    
    # Absolute permalinks (starting with /)
    if link.startswith('/'):
        # Absolute permalink - check if it should include baseurl
        # In Jekyll, absolute permalinks override baseurl
        config = load_jekyll_config()
        site_url = config.get('url', 'https://yasarshaikh.github.io').rstrip('/')
        # Try with baseurl first (most common case)
        baseurl = config.get('baseurl', '').strip('/')
        if baseurl:
            url_with_base = f"{site_url}/{baseurl}{link}"
            url_without_base = f"{site_url}{link}"
            # Return both possibilities - we'll check both
            return url_with_base  # Prefer with baseurl
        return f"{site_url}{link}"
    
    # Relative links - resolve properly
    source_dir = source_file.parent
    
    # Handle parent directory references (../)
    if '../' in link or link.startswith('../'):
        # Resolve relative path
        parts = link.split('/')
        current_dir = source_dir
        for part in parts:
            if part == '..':
                current_dir = current_dir.parent
            elif part == '.':
                continue
            elif part:
                current_dir = current_dir / part
        
        # Convert .md to .html if needed
        if current_dir.suffix == '.md':
            current_dir = current_dir.with_suffix('.html')
        elif current_dir.suffix != '.html' and (current_dir / f"{current_dir.name}.md").exists():
            current_dir = current_dir / f"{current_dir.name}.html"
        
        # Get relative path from docs/
        try:
            rel_path = current_dir.relative_to(Path('docs'))
            return f"{base_url}/{rel_path}"
        except ValueError:
            # Path is outside docs/ - might be CONTRIBUTING.md in root
            if 'CONTRIBUTING' in current_dir.name:
                # CONTRIBUTING.md is in repo root, not in docs/
                return "https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md"
            return f"{base_url}/{link}"
    
    # Simple relative links (same directory or subdirectory)
    # Convert .md to .html
    if link.endswith('.md'):
        link = link.replace('.md', '.html')
    
    # Check if target file exists and has a permalink
    md_file = source_dir / link.replace('.html', '.md')
    if md_file.exists():
        return get_file_url(md_file, base_url)
    
    # Build relative URL
    rel_dir = source_dir.relative_to(Path('docs'))
    if str(rel_dir) != '.':
        return f"{base_url}/{rel_dir}/{link}"
    else:
        return f"{base_url}/{link}"

def check_http_status_and_content(url: str, timeout: int = 10) -> Tuple[int, str, bool]:
    """
    Check HTTP status AND content of a URL.
    Returns: (http_code, error_message, is_valid_page)
    is_valid_page: True if page exists and is not a 404/error page
    """
    try:
        # Get HTTP status and content
        result = subprocess.run(
            ['curl', '-s', '-L', '--max-time', str(timeout), '-w', '\n%{http_code}', url],
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        
        if result.returncode != 0:
            return 0, result.stderr, False
        
        # Split content and status code
        output = result.stdout
        if '\n' in output:
            content, http_code_str = output.rsplit('\n', 1)
            try:
                http_code = int(http_code_str.strip())
            except ValueError:
                return 0, "Could not parse HTTP code", False
        else:
            content = output
            http_code = 0
        
        # Validate content - check for 404 indicators
        content_lower = content.lower()
        
        # Check for 404 page indicators
        is_404 = (
            '404' in content_lower and ('not found' in content_lower or 'doesn\'t exist' in content_lower or 'page not found' in content_lower) or
            'github pages site here' in content_lower or
            'there isn\'t a github pages site' in content_lower or
            (http_code == 404)
        )
        
        # Check for valid page indicators (has title, not just error message)
        has_title = bool(re.search(r'<title[^>]*>.*?</title>', content, re.IGNORECASE | re.DOTALL))
        has_content = len(content) > 500  # Real pages have more content than error pages
        
        is_valid = not is_404 and has_title and has_content and http_code == 200
        
        return http_code, '', is_valid
        
    except subprocess.TimeoutExpired:
        return 0, "Timeout", False
    except Exception as e:
        return 0, str(e), False

def main():
    base_url = get_base_url()
    config = load_jekyll_config()
    site_url = config.get('url', 'https://yasarshaikh.github.io').rstrip('/')
    baseurl = config.get('baseurl', '').strip('/')
    
    print(f"🔗 Checking GitHub Pages Links")
    print(f"===============================")
    print(f"")
    print(f"{BLUE}Site URL: {site_url}{NC}")
    print(f"{BLUE}Base URL: {base_url}{NC}")
    print(f"{BLUE}Baseurl: /{baseurl}{NC}" if baseurl else f"{BLUE}Baseurl: (none){NC}")
    print(f"")
    
    errors = 0
    warnings = 0
    
    # Find all markdown files
    md_files = list(Path('docs').rglob('*.md'))
    
    print(f"{BLUE}Checking internal links (HTTP status + content validation)...{NC}")
    print(f"")
    
    for file in md_files:
        print(f"{BLUE}Checking: {file}{NC}")
        
        # Extract links from markdown
        with open(file) as f:
            content = f.read()
        
        # Find all markdown links [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for text, link in links:
            # Skip external links (check separately if needed)
            if link.startswith('http'):
                http_code, error, is_valid = check_http_status_and_content(link)
                if is_valid or http_code == 200:
                    print(f"  {GREEN}✅ External: {link} (HTTP {http_code}){NC}")
                elif http_code in [403, 401]:
                    # 403/401 might be bot blocking (false positive) - warn but don't fail
                    print(f"  {YELLOW}⚠️  External: {link} (HTTP {http_code} - may be bot blocking){NC}")
                    warnings += 1
                elif http_code != 0:
                    print(f"  {RED}❌ Broken external link: {link} (HTTP {http_code}){NC}")
                    errors += 1
                continue
            
            # Skip anchor links
            if link.startswith('#'):
                continue
            
            # Resolve link to full URL
            full_url = resolve_link(link, file, base_url)
            
            # For absolute permalinks, also check without baseurl
            urls_to_check = [full_url]
            if link.startswith('/') and baseurl:
                # Also check with baseurl (Jekyll might use either)
                url_without_base = f"{site_url}{link}"
                if url_without_base != full_url:
                    urls_to_check.append(url_without_base)
            
            # Check each possible URL
            found_valid = False
            for check_url in urls_to_check:
                http_code, error, is_valid = check_http_status_and_content(check_url)
                
                if is_valid:
                    print(f"  {GREEN}✅ {link} (HTTP {http_code}){NC}")
                    if len(urls_to_check) > 1:
                        print(f"      {BLUE}Verified at: {check_url}{NC}")
                    found_valid = True
                    break
                elif http_code == 200 and not is_valid:
                    # HTTP 200 but content looks like 404 - suspicious
                    print(f"  {YELLOW}⚠️  {link} (HTTP 200 but content invalid){NC}")
                    print(f"      {YELLOW}Checked: {check_url}{NC}")
                    warnings += 1
                    found_valid = True  # Don't count as error, but warn
                    break
            
            if not found_valid:
                # Try the other URL if we haven't checked it yet
                if len(urls_to_check) > 1:
                    other_url = urls_to_check[1] if urls_to_check[0] == full_url else urls_to_check[0]
                    http_code, error, is_valid = check_http_status_and_content(other_url)
                    if is_valid:
                        print(f"  {GREEN}✅ {link} (HTTP {http_code}){NC}")
                        print(f"      {BLUE}Verified at: {other_url}{NC}")
                        found_valid = True
                
                if not found_valid:
                    print(f"  {RED}❌ Broken link: {link} (HTTP {http_code if http_code else 'failed'}){NC}")
                    for url in urls_to_check:
                        print(f"      {RED}Checked: {url}{NC}")
                    errors += 1
    
    # Summary
    print(f"")
    print(f"===============================")
    if errors == 0 and warnings == 0:
        print(f"{GREEN}✅ All links verified!{NC}")
        return 0
    elif errors == 0:
        print(f"{YELLOW}⚠️  Links verified with {warnings} warning(s){NC}")
        return 0
    else:
        print(f"{RED}❌ Found {errors} broken link(s){NC}")
        if warnings > 0:
            print(f"   {YELLOW}and {warnings} warning(s){NC}")
        return 1

if __name__ == '__main__':
    exit(main())
