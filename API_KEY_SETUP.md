# API Key Setup Guide
## krl-data-connectors

This guide explains how to set up API keys for the KRL Data Connectors in a portable, cross-platform manner.

---

## 🔑 API Keys Required

| Connector | API Key Required | Registration URL |
|-----------|------------------|------------------|
| **CBP** (County Business Patterns) | ❌ No | N/A |
| **LEHD** (Employment Dynamics) | ❌ No | N/A |
| **FRED** (Federal Reserve) | ✅ Yes | https://fred.stlouisfed.org/docs/api/api_key.html |
| **BLS** (Bureau of Labor Stats) | ⚠️  Recommended* | https://www.bls.gov/developers/home.htm |
| **BEA** (Bureau of Economic Analysis) | ✅ Yes | https://apps.bea.gov/api/signup/ |

*BLS works without a key but has strict rate limits (25 requests/day vs 500 with key)

---

## 📁 Configuration Options

The `krl-data-connectors` package supports multiple configuration methods, checked in this priority order:

### Option 1: Environment Variables (Recommended for Production)

```bash
# Linux/macOS
export BEA_API_KEY="your_bea_api_key"
export FRED_API_KEY="your_fred_api_key"
export BLS_API_KEY="your_bls_api_key"

# Windows (PowerShell)
$env:BEA_API_KEY="your_bea_api_key"
$env:FRED_API_KEY="your_fred_api_key"
$env:BLS_API_KEY="your_bls_api_key"

# Windows (Command Prompt)
set BEA_API_KEY=your_bea_api_key
set FRED_API_KEY=your_fred_api_key
set BLS_API_KEY=your_bls_api_key
```

**Make permanent:**
```bash
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
echo 'export BEA_API_KEY="your_bea_api_key"' >> ~/.bashrc
echo 'export FRED_API_KEY="your_fred_api_key"' >> ~/.bashrc
echo 'export BLS_API_KEY="your_bls_api_key"' >> ~/.bashrc
source ~/.bashrc

# Windows: Use System Properties → Environment Variables
```

### Option 2: Config File (Recommended for Development)

The package automatically searches for a config file named `apikeys` in these locations:

1. **`KRL_CONFIG_PATH` environment variable** (if set)
2. **`~/KR-Labs/Khipu/config/apikeys`** (KRL standard location)
3. **`~/.krl/apikeys`** (hidden config directory)
4. **`./config/apikeys`** (relative to current directory)

#### Create Config File

**Linux/macOS:**
```bash
# Option A: Standard KRL location
mkdir -p ~/KR-Labs/Khipu/config
cat > ~/KR-Labs/Khipu/config/apikeys << EOF
BEA API KEY: your_bea_api_key
FRED API KEY: your_fred_api_key
BLS API KEY: your_bls_api_key
CENSUS API: your_census_api_key
EOF

# Option B: Hidden config directory (more portable)
mkdir -p ~/.krl
cat > ~/.krl/apikeys << EOF
BEA API KEY: your_bea_api_key
FRED API KEY: your_fred_api_key
BLS API KEY: your_bls_api_key
CENSUS API: your_census_api_key
EOF

# Set permissions (keep keys private)
chmod 600 ~/.krl/apikeys
```

**Windows (PowerShell):**
```powershell
# Standard KRL location
New-Item -ItemType Directory -Force -Path "$HOME\KR-Labs\Khipu\config"
@"
BEA API KEY: your_bea_api_key
FRED API KEY: your_fred_api_key
BLS API KEY: your_bls_api_key
CENSUS API: your_census_api_key
"@ | Out-File -FilePath "$HOME\KR-Labs\Khipu\config\apikeys" -Encoding utf8

# OR: Hidden config directory
New-Item -ItemType Directory -Force -Path "$HOME\.krl"
@"
BEA API KEY: your_bea_api_key
FRED API KEY: your_fred_api_key
BLS API KEY: your_bls_api_key
CENSUS API: your_census_api_key
"@ | Out-File -FilePath "$HOME\.krl\apikeys" -Encoding utf8
```

#### Config File Format

```
BEA API KEY: 9D35B76D-D94E-47A2-9509-6D81CFDD4259
FRED API KEY: 8ec3c8309e60d874eae960d407f15460
BLS API KEY: 869945c941d14c65bb464751f51cee55
CENSUS API: 199343249e46333a2676a4976d696e45a9d2e15d
```

**Important:**
- One key per line
- Format: `API_NAME API KEY: key_value`
- No quotes needed
- Comments not supported

### Option 3: Direct in Code (Not Recommended for Production)

```python
from krl_data_connectors import BEAConnector, FREDConnector, BLSConnector

# Pass API key directly
bea = BEAConnector(api_key="your_bea_api_key")
fred = FREDConnector(api_key="your_fred_api_key")
bls = BLSConnector(api_key="your_bls_api_key")
```

⚠️ **Security Warning:** Never commit API keys to version control!

### Option 4: Custom Config Path

Set a custom location using environment variable:

```bash
export KRL_CONFIG_PATH="/path/to/your/custom/apikeys"
```

---

## 🧪 Verify Configuration

### Using Python

```python
from krl_data_connectors import find_config_file

# Check if config file is found
config_path = find_config_file('apikeys')
if config_path:
    print(f"✅ Config file found: {config_path}")
else:
    print("❌ No config file found")
    print("Create one at: ~/.krl/apikeys")
```

### Test Connectors

```python
import os
from krl_data_connectors import BEAConnector, FREDConnector, BLSConnector

# Test BEA
try:
    bea = BEAConnector()
    print("✅ BEA connector initialized")
except ValueError as e:
    print(f"❌ BEA failed: {e}")

# Test FRED
try:
    fred = FREDConnector()
    if fred.api_key:
        print("✅ FRED connector initialized with API key")
    else:
        print("⚠️  FRED initialized without API key")
except Exception as e:
    print(f"❌ FRED failed: {e}")

# Test BLS
try:
    bls = BLSConnector()
    if bls.api_key:
        print("✅ BLS connector initialized with API key (500 req/day)")
    else:
        print("⚠️  BLS initialized without API key (25 req/day)")
except Exception as e:
    print(f"❌ BLS failed: {e}")
```

---

## 🔒 Security Best Practices

### 1. Never Commit Keys to Version Control

Add to `.gitignore`:
```bash
# Add these to .gitignore
config/apikeys
.env
*.key
*apikeys*
```

### 2. Use Different Keys for Different Environments

```bash
# Development
export BEA_API_KEY="dev_key_here"

# Production
export BEA_API_KEY="prod_key_here"
```

### 3. Rotate Keys Regularly

- Review API usage monthly
- Rotate keys every 6-12 months
- Revoke old keys after rotation

### 4. Set Proper File Permissions

```bash
# Make config file readable only by you
chmod 600 ~/.krl/apikeys

# Verify permissions
ls -l ~/.krl/apikeys
# Should show: -rw------- (read/write for owner only)
```

### 5. Use Key Vaults in Production

For production deployments:
- **AWS**: AWS Secrets Manager
- **Azure**: Azure Key Vault
- **GCP**: Google Secret Manager
- **Docker**: Docker secrets

Example with AWS Secrets Manager:
```python
import boto3
import json
from krl_data_connectors import BEAConnector

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('krl-api-keys')
bea = BEAConnector(api_key=secrets['BEA_API_KEY'])
```

---

## 🐳 Docker Configuration

### Using Environment Variables

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Pass API keys at runtime
CMD ["python", "your_script.py"]
```

Run with:
```bash
docker run \
  -e BEA_API_KEY="your_key" \
  -e FRED_API_KEY="your_key" \
  -e BLS_API_KEY="your_key" \
  your-image:latest
```

### Using Docker Secrets

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: your-image:latest
    secrets:
      - bea_api_key
      - fred_api_key
      - bls_api_key
    environment:
      BEA_API_KEY_FILE: /run/secrets/bea_api_key
      FRED_API_KEY_FILE: /run/secrets/fred_api_key
      BLS_API_KEY_FILE: /run/secrets/bls_api_key

secrets:
  bea_api_key:
    file: ./secrets/bea_key.txt
  fred_api_key:
    file: ./secrets/fred_key.txt
  bls_api_key:
    file: ./secrets/bls_key.txt
```

---

## 🌐 CI/CD Configuration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        env:
          BEA_API_KEY: ${{ secrets.BEA_API_KEY }}
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
          BLS_API_KEY: ${{ secrets.BLS_API_KEY }}
        run: pytest tests/
```

Add secrets in GitHub: **Settings → Secrets and variables → Actions → New repository secret**

### GitLab CI

```yaml
test:
  stage: test
  image: python:3.11
  variables:
    BEA_API_KEY: ${BEA_API_KEY}
    FRED_API_KEY: ${FRED_API_KEY}
    BLS_API_KEY: ${BLS_API_KEY}
  script:
    - pip install -r requirements.txt
    - pytest tests/
```

Add secrets in GitLab: **Settings → CI/CD → Variables**

---

## ❓ Troubleshooting

### "No config file found"

**Problem:** Config file not in expected locations

**Solution:**
```bash
# Check which locations are being searched
python -c "from krl_data_connectors import find_config_file; print(find_config_file.__doc__)"

# Create config in standard location
mkdir -p ~/.krl
echo "BEA API KEY: your_key" > ~/.krl/apikeys
```

### "API key not found" even though config exists

**Problem:** Wrong format in config file

**Solution:** Check format exactly matches:
```
BEA API KEY: your_key_here
```
NOT:
```
BEA_API_KEY=your_key_here  # ❌ Wrong format
bea api key: your_key      # ❌ Case sensitive
BEA API KEY:your_key       # ❌ Missing space after colon
```

### "Permission denied" when reading config

**Problem:** File permissions too restrictive

**Solution:**
```bash
chmod 600 ~/.krl/apikeys  # Owner read/write only
```

### Keys work locally but not in notebooks

**Problem:** Jupyter kernel doesn't see environment variables

**Solution:** Restart Jupyter kernel or use config file method instead

---

## 📚 Additional Resources

- **BEA API Documentation**: https://apps.bea.gov/api/
- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/
- **BLS API Documentation**: https://www.bls.gov/developers/
- **KRL Data Connectors GitHub**: https://github.com/KR-Labs/krl-data-connectors

---

## 📝 Quick Start Checklist

- [ ] Register for API keys (BEA, FRED, BLS)
- [ ] Choose configuration method (env vars or config file)
- [ ] Create config file at `~/.krl/apikeys`
- [ ] Add keys to config file
- [ ] Set file permissions: `chmod 600 ~/.krl/apikeys`
- [ ] Add `*apikeys*` to `.gitignore`
- [ ] Test configuration with example notebook
- [ ] Set up key rotation schedule

---

*Last Updated: October 19, 2025*  
*© 2025 KR-Labs. All rights reserved.*
