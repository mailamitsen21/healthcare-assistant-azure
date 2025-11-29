# Prerequisites Setup Guide

## 🔧 Required Tools Installation

Before deploying, you need to install these tools:

### 1. Azure CLI (az)

**For macOS (using Homebrew - Recommended):**

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Azure CLI
brew install azure-cli

# Verify installation
az --version
```

**Alternative - Direct Download:**
1. Download from: https://aka.ms/installazureclimac
2. Run the installer package
3. Restart your terminal

**After installation:**
```bash
# Login to Azure
az login

# Verify you're logged in
az account show
```

### 2. Azure Functions Core Tools

**For macOS:**

```bash
# Install using npm (requires Node.js)
npm install -g azure-functions-core-tools@4

# Or using Homebrew
brew tap azure/functions
brew install azure-functions-core-tools@4

# Verify installation
func --version
```

**Note:** If you don't have Node.js:
```bash
# Install Node.js first
brew install node
```

### 3. Python 3.11+

**Check if you have Python:**
```bash
python3 --version
```

**If you need to install/upgrade:**
```bash
# Using Homebrew
brew install python@3.11

# Or download from: https://www.python.org/downloads/
```

### 4. Git (for deployment)

**Check if you have Git:**
```bash
git --version
```

**If you need to install:**
```bash
brew install git
```

## ✅ Quick Setup Script

Run this to install everything at once (if you have Homebrew):

```bash
# Install all prerequisites
brew install azure-cli node python@3.11 git

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Verify all installations
echo "Checking installations..."
az --version
func --version
python3 --version
git --version
```

## 🔐 After Installation

1. **Login to Azure:**
   ```bash
   az login
   ```
   This will open a browser window for authentication.

2. **Set your subscription (if you have multiple):**
   ```bash
   # List subscriptions
   az account list --output table
   
   # Set active subscription
   az account set --subscription "4188ef75-9e34-4fa8-b24f-1ef2d53a09df"
   ```

3. **Verify you're ready:**
   ```bash
   # Check Azure login
   az account show
   
   # Check Function Tools
   func --version
   
   # Check Python
   python3 --version
   ```

## 🚀 Once Everything is Installed

You can proceed with deployment:

```bash
# Option 1: Use the automated script
./deploy.sh

# Option 2: Follow manual steps in DEPLOY_NOW.md
```

## 🆘 Troubleshooting

### Azure CLI Issues

**If `az` command not found after installation:**
```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**If login fails:**
```bash
# Try clearing cache
az account clear
az login
```

### Azure Functions Core Tools Issues

**If `func` command not found:**
```bash
# Check npm global path
npm config get prefix

# Add to PATH if needed
export PATH="$(npm config get prefix)/bin:$PATH"
```

**If you get permission errors:**
```bash
# Fix npm permissions (macOS)
sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}
```

### Python Issues

**If Python version is wrong:**
```bash
# Check which Python
which python3

# Use specific version
python3.11 --version
```

## 📋 Installation Checklist

- [ ] Azure CLI installed (`az --version` works)
- [ ] Azure CLI logged in (`az account show` works)
- [ ] Azure Functions Core Tools installed (`func --version` works)
- [ ] Python 3.11+ installed (`python3 --version` shows 3.11+)
- [ ] Git installed (`git --version` works)
- [ ] Node.js installed (for npm, `node --version` works)

Once all checkboxes are checked, you're ready to deploy! 🎉

