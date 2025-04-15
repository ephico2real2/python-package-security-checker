#!/usr/bin/env python3
"""
Security Check Example - Demonstrate concurrent package version checking with security focus

python3 -m venv venv && source venv/bin/activate && pip install requests packaging 

pip install --upgrade pip

pip install aiohttp

This advanced script demonstrates:
1. Concurrent package checking using asyncio and aiohttp
2. Security sensitivity checking based on package categories
3. Handling of both standard and non-standard version numbers
4. Processing multiple packages simultaneously with timing information
"""

import sys
import argparse
import asyncio
import time
from datetime import datetime
from packaging import version

try:
    import aiohttp
except ImportError:
    print("This script requires aiohttp. Install it with: pip install aiohttp")
    sys.exit(1)

# List of known security-sensitive packages
SECURITY_SENSITIVE_PACKAGES = {
    "django",
    "cryptography",
    "requests",
    "urllib3",
    "pillow",
    "pyyaml",
    "werkzeug",
    "jinja2",
    "flask",
    "sqlalchemy",
    "celery",
}

class PackageInfo:
    """Store package information and update status."""
    
    def __init__(self, name, current_version=None):
        self.name = name
        self.current_version = current_version
        self.latest_version = None
        self.release_date = None
        self.update_type = None
        self.is_security_sensitive = name.lower() in SECURITY_SENSITIVE_PACKAGES
        self.error = None
        
    def determine_update_type(self):
        """Determine the type of update needed (MAJOR, MINOR, PATCH, NONE)."""
        if not self.current_version or not self.latest_version:
            return "UNKNOWN"
            
        if self.current_version == self.latest_version:
            return "NONE"
            
        try:
            current = version.parse(self.current_version)
            latest = version.parse(self.latest_version)
            
            # Handle pre-releases and non-standard versions
            if not hasattr(current, 'release') or not hasattr(latest, 'release'):
                # For non-standard versions, compare as strings
                return "UPDATE_AVAILABLE" if latest > current else "NONE"
            
            # If current version has more or fewer parts than latest
            if len(current.release) != len(latest.release):
                max_length = max(len(current.release), len(latest.release))
                # Pad with zeros
                current_parts = list(current.release) + [0] * (max_length - len(current.release))
                latest_parts = list(latest.release) + [0] * (max_length - len(latest.release))
            else:
                current_parts = current.release
                latest_parts = latest.release
            
            # Compare parts to determine update type
            for i, (c, l) in enumerate(zip(current_parts, latest_parts)):
                if l > c:
                    if i == 0:
                        return "MAJOR"
                    elif i == 1:
                        return "MINOR"
                    else:
                        return "PATCH"
                elif c > l:
                    # Current is ahead of latest (unusual case)
                    return "CURRENT_AHEAD"
            
            return "NONE"  # Identical versions
            
        except Exception as e:
            self.error = f"Version comparison error: {e}"
            return "ERROR"

    def get_update_emoji(self):
        """Return an emoji representing the update type."""
        if not self.update_type or self.update_type == "NONE":
            return "✅"
        if self.update_type == "MAJOR":
            return "⚠️"
        if self.update_type == "MINOR":
            return "ℹ️"
        if self.update_type == "PATCH":
            return "🔧"
        if self.update_type == "CURRENT_AHEAD":
            return "⏮️"
        if self.update_type == "ERROR":
            return "❌"
        return "⚠️"  # Default for unknown states
        
    def get_update_priority(self):
        """Return update priority based on type and security sensitivity."""
        if self.update_type == "NONE":
            return 0
            
        # Base priority on update type
        priority = {
            "MAJOR": 30,
            "MINOR": 20,
            "PATCH": 10,
            "UPDATE_AVAILABLE": 25,  # For non-standard versions
            "CURRENT_AHEAD": 5,
            "ERROR": 1,
            "UNKNOWN": 1
        }.get(self.update_type, 0)
        
        # Increase priority for security-sensitive packages
        if self.is_security_sensitive:
            priority += 50
            
        return priority
        
    def __str__(self):
        """Return a formatted string representation of the package info."""
        if self.error:
            return f"{self.name}: ERROR - {self.error}"
            
        status = []
        status.append(f"{self.get_update_emoji()} {self.name}")
        
        if self.current_version:
            status.append(f"{self.current_version} → {self.latest_version or 'unknown'}")
        else:
            status.append(f"Latest: {self.latest_version or 'unknown'}")
            
        if self.release_date:
            try:
                dt = datetime.fromisoformat(self.release_date.replace('Z', '+00:00'))
                date_str = dt.strftime("%Y-%m-%d")
                status.append(f"Released: {date_str}")
            except (ValueError, TypeError):
                status.append(f"Released: {self.release_date}")
                
        if self.is_security_sensitive:
            status.append("🔒 SECURITY-SENSITIVE")
            
        if self.update_type and self.update_type != "NONE":
            status.append(f"Update type: {self.update_type}")
            
        return " | ".join(status)


async def fetch_package_info(session, package, timeout=10):
    """Fetch package information from PyPI asynchronously."""
    url = f"https://pypi.org/pypi/{package.name}/json"
    
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 404:
                package.error = "Package not found on PyPI"
                return package
                
            response.raise_for_status()
            data = await response.json()
            
            package.latest_version = data["info"]["version"]
            
            # Get upload date of the latest version
            release_info = data["releases"][package.latest_version]
            if release_info:
                package.release_date = release_info[0]["upload_time_iso_8601"]
                
            if package.current_version:
                package.update_type = package.determine_update_type()
                
            return package
                
    except asyncio.TimeoutError:
        package.error = f"Request timed out after {timeout} seconds"
    except aiohttp.ClientError as e:
        package.error = f"Request error: {e}"
    except (KeyError, ValueError, IndexError) as e:
        package.error = f"Error parsing response: {e}"
    except Exception as e:
        package.error = f"Unexpected error: {e}"
        
    return package


async def check_packages(packages, timeout=10, max_workers=5):
    """Check multiple packages concurrently."""
    start_time = time.time()
    
    # Set up connection pooling for better performance
    conn = aiohttp.TCPConnector(limit=max_workers)
    async with aiohttp.ClientSession(connector=conn) as session:
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_workers)
        
        async def fetch_with_semaphore(package):
            async with semaphore:
                return await fetch_package_info(session, package, timeout)
                
        # Create tasks for all packages
        tasks = [fetch_with_semaphore(pkg) for pkg in packages]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
    elapsed = time.time() - start_time
    return results, elapsed


def format_results(results, show_all=False):
    """Format and sort results for display."""
    # Sort by priority (security-sensitive and update type)
    sorted_results = sorted(
        results, 
        key=lambda p: (-p.get_update_priority(), p.name.lower())
    )
    
    # Filter out packages with no updates unless show_all is True
    if not show_all:
        sorted_results = [p for p in sorted_results if p.get_update_priority() > 0]
        
    return sorted_results


def parse_requirements(filename):
    """Parse a requirements.txt file into package name and version."""
    packages = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle requirement format 'package==version'
                if '==' in line:
                    name, version = line.split('==', 1)
                    packages.append(PackageInfo(name.strip(), version.strip()))
                # Handle requirement format 'package>=version'
                elif '>=' in line:
                    name, version = line.split('>=', 1)
                    packages.append(PackageInfo(name.strip(), version.strip()))
                # Handle package with no version specified
                else:
                    packages.append(PackageInfo(line.strip()))
    except Exception as e:
        print(f"Error parsing requirements file: {e}")
        
    return packages


def generate_updated_requirements(input_file, output_file, results, security_only=False):
    """Generate updated requirements.txt file with latest versions."""
    if not input_file or not output_file:
        return False
        
    # Create a dictionary of package results for quick lookup
    pkg_results = {p.name.lower(): p for p in results}
    
    try:
        # Read the original file
        with open(input_file, 'r') as f:
            lines = f.readlines()
            
        # Open the output file
        with open(output_file, 'w') as f:
            # Add metadata header
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"# Updated requirements file generated on {now}\n")
            f.write(f"# Original file: {input_file}\n")
            if security_only:
                f.write("# Only security-sensitive packages were updated\n")
            else:
                f.write("# All packages were updated to their latest versions\n")
            f.write("#\n\n")
            
            # Process each line from the original file
            for line in lines:
                line = line.rstrip('\n')
                # Skip empty lines and comments
                if not line or line.strip().startswith('#'):
                    f.write(f"{line}\n")
                    continue
                    
                # Check if line contains a package specification
                if '==' in line:
                    pkg_name, _ = line.split('==', 1)
                    pkg_name = pkg_name.strip().lower()
                    
                    # Check if we have an update for this package
                    if pkg_name in pkg_results:
                        pkg = pkg_results[pkg_name]
                        if pkg.latest_version and (not security_only or pkg.is_security_sensitive):
                            # Update the version
                            line = f"{pkg_name}=={pkg.latest_version}"
                            
                elif '>=' in line:
                    pkg_name, _ = line.split('>=', 1)
                    pkg_name = pkg_name.strip().lower()
                    
                    # For >= specifications, only update if it's security-sensitive
                    if pkg_name in pkg_results and pkg_results[pkg_name].is_security_sensitive and security_only:
                        pkg = pkg_results[pkg_name]
                        if pkg.latest_version:
                            line = f"{pkg_name}>={pkg.latest_version}"
                            
                else:
                    # Package without version specification
                    pkg_name = line.strip().lower()
                    if pkg_name in pkg_results:
                        pkg = pkg_results[pkg_name]
                        if pkg.latest_version and (not security_only or pkg.is_security_sensitive):
                            line = f"{pkg_name}=={pkg.latest_version}"
                            
                f.write(f"{line}\n")
                
        return True
        
    except Exception as e:
        print(f"Error generating updated requirements file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check packages for updates with focus on security-sensitive packages"
    )
    parser.add_argument(
        "packages", 
        nargs="*", 
        help="Package names to check (can also use -r for requirements file)"
    )
    parser.add_argument(
        "-r", "--requirements", 
        help="Path to requirements.txt file"
    )
    parser.add_argument(
        "-t", "--timeout", 
        type=int, 
        default=10, 
        help="HTTP request timeout in seconds"
    )
    parser.add_argument(
        "-w", "--workers", 
        type=int, 
        default=5, 
        help="Maximum number of concurrent requests"
    )
    parser.add_argument(
        "-a", "--all", 
        action="store_true", 
        help="Show all packages, including those with no updates"
    )
    parser.add_argument(
        "-o", "--output-file",
        help="Generate updated requirements file with latest versions"
    )
    parser.add_argument(
        "-s", "--update-security-only",
        action="store_true",
        help="When generating updated requirements, only update security-sensitive packages"
    )
    
    args = parser.parse_args()
    
    packages = []
    
    # Parse requirements file if provided
    if args.requirements:
        packages.extend(parse_requirements(args.requirements))
        
    # Add individual packages from command line
    for pkg in args.packages:
        if '==' in pkg:
            name, version = pkg.split('==', 1)
            packages.append(PackageInfo(name.strip(), version.strip()))
        else:
            packages.append(PackageInfo(pkg.strip()))
            
    if not packages:
        print("No packages specified. Use -r to specify a requirements file or provide package names.")
        parser.print_help()
        return 1
        
    print(f"Checking {len(packages)} packages (max {args.workers} concurrent workers)...")
    
    # Run the async check
    loop = asyncio.get_event_loop()
    results, elapsed = loop.run_until_complete(
        check_packages(packages, args.timeout, args.workers)
    )
    
    # Format and display results
    sorted_results = format_results(results, args.all)
    
    print(f"\nResults ({elapsed:.2f} seconds):")
    print("=" * 70)
    
    # Count security-sensitive packages with updates
    security_updates = sum(1 for p in sorted_results if p.is_security_sensitive and p.get_update_priority() > 0)
    if security_updates > 0:
        print(f"🔒 {security_updates} security-sensitive packages need updates!\n")
        
    # Print all results
    for pkg in sorted_results:
        print(pkg)
        
    # Print summary
    updates_needed = sum(1 for p in results if p.get_update_priority() > 0)
    errors = sum(1 for p in results if p.error)
    
    print("\nSummary:")
    print(f"Total packages checked: {len(packages)}")
    print(f"Packages needing updates: {updates_needed}")
    print(f"Security-sensitive packages needing updates: {security_updates}")
    print(f"Errors: {errors}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    
    # Generate updated requirements file if requested
    if args.output_file and args.requirements:
        if generate_updated_requirements(args.requirements, args.output_file, results, args.update_security_only):
            print(f"\nUpdated requirements file generated: {args.output_file}")
        else:
            print(f"\nFailed to generate updated requirements file")
    
    # Return non-zero exit code if security updates are needed
    return 1 if security_updates > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

