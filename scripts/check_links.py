#!/usr/bin/env python3
"""
Robust link checker for GitHub Pages documentation.
Uses HTTP status verification (like a crawler) and properly handles Jekyll permalinks.
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
        if permalink.startswith('/'):
            return f"{base_url}{permalink}"
        else:
            return f"{base_url}/{permalink}"
    
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
        return f"{base_url}{link}"
    
    # Relative links
    source_dir = source_file.parent
    target_path = source_dir / link
    
    # Convert .md to .html
    if link.endswith('.md'):
        target_path = source_dir / link.replace('.md', '.html')
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

def check_http_status(url: str, timeout: int = 5) -> Tuple[int, str]:
    """Check HTTP status of a URL using curl"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-L', '--max-time', str(timeout), url],
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        http_code = result.stdout.strip()
        if http_code.isdigit():
            return int(http_code), ''
        return 0, result.stderr
    except Exception as e:
        return 0, str(e)

def main():
    base_url = get_base_url()
    print(f"🔗 Checking GitHub Pages Links")
    print(f"===============================")
    print(f"")
    print(f"{BLUE}Base URL: {base_url}{NC}")
    print(f"")
    
    errors = 0
    warnings = 0
    
    # Find all markdown files
    md_files = list(Path('docs').rglob('*.md'))
    
    print(f"{BLUE}Checking internal links (HTTP status verification)...{NC}")
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
                http_code, error = check_http_status(link)
                if http_code == 200:
                    print(f"  {GREEN}✅ External: {link} (HTTP 200){NC}")
                elif http_code != 0:
                    print(f"  {RED}❌ Broken external link: {link} (HTTP {http_code}){NC}")
                    errors += 1
                continue
            
            # Skip anchor links
            if link.startswith('#'):
                continue
            
            # Resolve link to full URL
            full_url = resolve_link(link, file, base_url)
            
            # Check HTTP status
            http_code, error = check_http_status(full_url)
            
            if http_code == 200:
                print(f"  {GREEN}✅ {link} (HTTP 200){NC}")
            elif http_code == 404:
                print(f"  {RED}❌ Broken link: {link} (HTTP 404){NC}")
                print(f"      {RED}Checked URL: {full_url}{NC}")
                errors += 1
            elif http_code == 0:
                # Network error - check local file
                if link.startswith('/'):
                    # Try to find file with this permalink
                    found = False
                    for md_file in md_files:
                        fm = extract_frontmatter(md_file)
                        if fm and fm.get('permalink') == link:
                            found = True
                            break
                    if found:
                        print(f"  {YELLOW}⚠️  {link} (local file exists, HTTP check failed - network issue?){NC}")
                        warnings += 1
                    else:
                        print(f"  {RED}❌ Broken link: {link} (HTTP check failed, file not found){NC}")
                        print(f"      {RED}Checked URL: {full_url}{NC}")
                        errors += 1
                else:
                    # Relative link - check local file
                    source_dir = file.parent
                    target_file = source_dir / link.replace('.html', '.md')
                    if target_file.exists():
                        print(f"  {YELLOW}⚠️  {link} (local file exists, HTTP check failed - network issue?){NC}")
                        warnings += 1
                    else:
                        print(f"  {RED}❌ Broken link: {link} (HTTP check failed, file not found){NC}")
                        print(f"      {RED}Checked URL: {full_url}{NC}")
                        errors += 1
            else:
                print(f"  {RED}❌ Broken link: {link} (HTTP {http_code}){NC}")
                print(f"      {RED}Checked URL: {full_url}{NC}")
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
