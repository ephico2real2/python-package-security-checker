# Python Package Security Checker

A comprehensive tool for checking and updating Python package dependencies with a focus on security-sensitive packages.

## Overview and Purpose

The `security_check.py` script is designed to help Python developers maintain secure and up-to-date dependencies by:

1. **Identifying outdated packages** in your Python projects
2. **Highlighting security-sensitive packages** that need updates
3. **Categorizing updates** by severity (MAJOR, MINOR, PATCH)
4. **Concurrently checking** multiple packages for better performance
5. **Generating updated requirements files** with the latest versions

This tool is particularly valuable for security-conscious teams and projects that need to maintain compliance with security standards or perform regular dependency audits.

## Quick Start

For the impatient, here's the fastest way to get started:

```bash
# Get the script and requirements
curl -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/security_check.py
curl -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/script_requirements.txt

# Install dependencies
pip install -r script_requirements.txt

# Check packages in requirements.txt
python security_check.py -r requirements.txt

# Or check specific packages
python security_check.py django cryptography requests
```

## Dependencies and Why They're Needed

The script requires the following dependencies:

- **aiohttp**: For making concurrent HTTP requests to PyPI, significantly improving performance when checking many packages
- **packaging**: Provides version parsing and comparison functionality to determine update types
- **asyncio**: Enables asynchronous programming for concurrent package checking

These dependencies are intentionally minimal to make the script easy to install and use. The script checks for the required dependencies at runtime and provides clear error messages if they're missing.

## Installation

### Option 1: Using the Setup Script (Recommended)

The easiest way to get started is with the included setup script, which creates a virtual environment and installs all dependencies:

```bash
# Clone the repository
git clone https://github.com/ephico2real2/python-package-security-checker.git
cd python-package-security-checker

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment (if not already activated by the script)
source venv/bin/activate
```

### Option 2: Manual Setup with Virtual Environment

If you prefer to set up the virtual environment manually:

```bash
# Clone the repository
git clone https://github.com/ephico2real2/python-package-security-checker.git
cd python-package-security-checker

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install required dependencies
pip install -r script_requirements.txt
```

### Option 3: Direct Installation

The script comes with a `script_requirements.txt` file that includes all necessary dependencies with proper version constraints:

```bash
# Clone the repository (or download both the script and requirements file)
git clone https://github.com/ephico2real2/python-package-security-checker.git
cd python-package-security-checker

# Install required dependencies using the requirements file
pip install -r script_requirements.txt
```

## Environment Compatibility

The Python Package Security Checker is designed to work across different environments:

- **Python Versions**: Compatible with Python 3.7 and above
- **Operating Systems**: Works on Linux, macOS, and Windows
  - **CI/CD Integration**: Can be integrated with GitHub Actions, GitLab CI, Jenkins, etc.
  - **Virtual Environments**: Works with virtualenv, venv, conda, and other Python environment managers
  - **Network Requirements**: Requires internet access to query PyPI for package information

### Virtual Environment Recommendations

For the most reliable and isolated experience, we recommend using a virtual environment:

1. **Isolation**: Prevents conflicts with system packages
2. **Clean testing**: Ensures all dependencies are explicitly installed
3. **Reproducibility**: Makes it easier to recreate the environment on other systems
4. **Safety**: Allows safe experimentation with package versions

The included `setup.sh` script creates and configures a virtual environment automatically.

## Usage Examples

If you only have the script without the requirements file:

```bash
# Install required dependencies directly
pip install aiohttp>=3.8.0 packaging>=21.0
```

### Alternative 2: Quick install for the script only

```bash
# Download the script
curl -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/security_check.py

# Make the script executable
chmod +x security_check.py

# Download the requirements file
curl -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/script_requirements.txt

# Install required dependencies
pip install -r script_requirements.txt
```

## Usage Examples

### Basic Usage

Check a list of packages specified directly on the command line:

```bash
python security_check.py django requests cryptography
```

### Check Packages from Requirements File

Check all packages in a requirements.txt file:

```bash
python security_check.py -r requirements.txt
```

### Show All Packages (Including Up-to-Date)

By default, the script only shows packages that need updates. Use the `-a` flag to show all packages:

```bash
python security_check.py -r requirements.txt -a
```

### Generate Updated Requirements File

Generate an updated requirements file with the latest versions:

```bash
python security_check.py -r requirements.txt -o requirements.updated.txt
```

### Update Only Security-Sensitive Packages

Generate an updated requirements file but only update security-sensitive packages:

```bash
python security_check.py -r requirements.txt -o requirements.updated.txt -s
```

### Increase Concurrency for Large Projects

For large requirements files, increase the number of concurrent workers:

```bash
python security_check.py -r requirements.txt -w 10
```

### Adjust Request Timeout

For slow connections, increase the HTTP request timeout:

```bash
python security_check.py -r requirements.txt -t 20
```

### Real-World Examples

#### CI/CD Pipeline Integration

```yaml
# In GitHub Actions workflow (.github/workflows/security-check.yml)
name: Security Check

on:
  schedule:
    - cron: '0 7 * * 1'  # Run every Monday at 7 AM
  workflow_dispatch:  # Allow manual trigger

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r script_requirements.txt
      - name: Run security check
        run: |
          python security_check.py -r requirements.txt
          if [ $? -eq 1 ]; then
            echo "::warning::Security updates needed!"
          fi
```

#### Scheduled Monitoring Script

```bash
#!/bin/bash
# security-monitor.sh
# Usage: Add to crontab with: 0 9 * * * /path/to/security-monitor.sh

# Navigate to project directory
cd /path/to/project

# Activate virtual environment
source venv/bin/activate

# Run security check and notify if updates needed
python security_check.py -r requirements.txt
if [ $? -eq 1 ]; then
  # Send email notification using mailx
  echo "Security updates needed for Python dependencies. Check output at: $(pwd)/security-report.txt" | \
  mail -s "SECURITY ALERT: Python package updates required" your-email@example.com
  
  # Generate report with details
  python security_check.py -r requirements.txt -a > security-report.txt
fi
```

#### Django Project Updates

```bash
# For a Django project with multiple requirements files

# Check all requirements files
for req_file in requirements/*.txt; do
  echo "Checking $req_file..."
  python security_check.py -r "$req_file" -o "${req_file%.txt}.updated.txt"
done

# Focus on security-sensitive updates only for production
python security_check.py -r requirements/production.txt -o requirements/production.secure.txt -s
```

## Output Explanation

The script produces output in several sections:

### Results Section

```
Results (0.25 seconds):
======================================================================
🔒 9 security-sensitive packages need updates!

⚠️ cryptography | 41.0.0 → 44.0.2 | Released: 2025-03-02 | 🔒 SECURITY-SENSITIVE | Update type: MAJOR
ℹ️ requests | 2.31.0 → 2.32.3 | Released: 2024-05-29 | 🔒 SECURITY-SENSITIVE | Update type: MINOR
🔧 sqlalchemy | 2.0.0 → 2.0.40 | Released: 2025-03-27 | 🔒 SECURITY-SENSITIVE | Update type: PATCH
```

The output includes:
- **Emoji indicators**: 
  - ⚠️ Major updates (potentially breaking changes)
  - ℹ️ Minor updates (new features, non-breaking)
  - 🔧 Patch updates (bug fixes only)
  - ✅ Up-to-date packages
- **Package info**: Name, current version, latest version
- **Release date**: When the latest version was released
- **Security indicator**: 🔒 marks security-sensitive packages
- **Update type**: MAJOR, MINOR, or PATCH

### Summary Section

```
Summary:
Total packages checked: 12
Packages needing updates: 9
Security-sensitive packages needing updates: 4
Errors: 0
Time elapsed: 0.25 seconds
```

Provides a quick overview of the scan results and performance.

## Common Use Cases

### 1. Regular Security Audits

Run the script weekly or monthly to ensure your dependencies stay secure:

```bash
# Add to your CI/CD pipeline or cron job
python security_check.py -r requirements.txt
```

### 2. Pre-Deployment Check

Before deploying to production, verify you don't have vulnerable dependencies:

```bash
python security_check.py -r requirements.txt && echo "Safe to deploy" || echo "Fix security issues first"
```

### 3. Generating Security-Focused Updates

Update only security-sensitive packages to minimize breaking changes:

```bash
python security_check.py -r requirements.txt -o requirements.secure.txt -s
```

### 4. Comprehensive Dependency Updates

Generate a completely updated requirements file during major version upgrades:

```bash
python security_check.py -r requirements.txt -o requirements.latest.txt
```

## Tips and Best Practices

1. **Prioritize security-sensitive updates**: Focus first on packages marked with 🔒

2. **Be cautious with MAJOR updates**: These may include breaking changes that require code modifications

3. **Use virtual environments**: Always test updates in an isolated environment before applying to production

4. **Generate pinned requirements**: When generating updated files, the script pins exact versions (`==`) for better reproducibility

5. **Keep the script updated**: The list of security-sensitive packages may change over time

6. **Schedule regular checks**: Automate security checks in your CI/CD pipeline or with scheduled tasks

7. **Review changelogs**: Before applying updates, review the changelogs of major packages

8. **Incremental updates**: For large projects, consider updating security-sensitive packages first, then moving to others

9. **Testing**: Always run your test suite after updating dependencies

10. **Version control**: Commit updated requirements files to version control only after testing

## Exit Codes

The script returns exit code `1` if security updates are needed, otherwise `0`. This can be used in CI/CD pipelines to fail builds when security issues are detected.

## Troubleshooting

### Common Issues and Solutions

1. **"Module not found" errors**:
   ```
   ModuleNotFoundError: No module named 'aiohttp'
   ```
   **Solution**: Install required dependencies with `pip install -r script_requirements.txt`

2. **Connection timeout errors**:
   ```
   Task was destroyed but it is pending!
   ```
   **Solution**: Increase timeout with the `-t` flag, e.g., `python security_check.py -r requirements.txt -t 30`

3. **Can't resolve package versions**:
   ```
   Warning: Failed to check package 'private-package': 404 Client Error
   ```
   **Solution**: The script only works with packages published on PyPI. For private packages, add them to an ignore list or modify your requirements file.

4. **Script seems to hang**:
   **Solution**: For large requirements files, increase concurrency with `-w` and add verbose output with `-v` to see progress.

5. **Too many packages shown in output**:
   **Solution**: By default, all outdated packages are shown. Use filtering flags like `-s` to show only security-sensitive updates.

### Debugging

If you encounter issues, try running with the `--verbose` flag for additional debug information:

```bash
python security_check.py -r requirements.txt --verbose
```

For very large requirements files, try breaking them into smaller files and checking each separately.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

