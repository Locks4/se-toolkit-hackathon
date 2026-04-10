# Auto Installer Script for Goal Tracker App
# This script downloads and installs Python and Node.js if they're missing

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Download-WithProgress {
    param([string]$Url, [string]$Output)
    
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "PowerShell Download")
        
        # Register progress event
        $ProgressPreference = 'Continue'
        $webClient.DownloadFile($Url, $Output)
        return $true
    } catch {
        try {
            # Fallback method
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $Url -OutFile $Output -UseBasicParsing
            return $true
        } catch {
            return $false
        }
    }
}

# Check if Python is installed
Write-Step "Checking Python..."
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if ($pythonInstalled) {
    Write-Host "Python is already installed!" -ForegroundColor Green
    python --version
} else {
    Write-Host "Python not found. Downloading and installing..." -ForegroundColor Yellow
    
    # Create temp directory
    $tempDir = "$env:TEMP\python_installer"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    }
    
    # Download Python installer
    $url = "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
    $output = "$tempDir\python-installer.exe"
    
    Write-Host "Downloading Python 3.12.1..." -ForegroundColor Cyan
    Write-Host "(This may take a minute depending on your internet speed)" -ForegroundColor Gray
    Write-Host ""
    
    if (Download-WithProgress -Url $url -Output $output) {
        Write-Host "Download complete!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to download Python installer" -ForegroundColor Red
        Write-Host "Please install manually from: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
    
    # Install Python silently
    Write-Host "Installing Python (this may take a few minutes)..." -ForegroundColor Yellow
    $process = Start-Process -FilePath $output -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_launcher=1", "Include_test=0" -Wait -PassThru
    
    # Cleanup
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "Python installed successfully!" -ForegroundColor Green
        python --version
    } else {
        Write-Host "WARNING: Python installation may have failed" -ForegroundColor Red
        Write-Host "Please install manually from: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
}

# Check if Node.js is installed
Write-Step "Checking Node.js..."
$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue
if ($nodeInstalled) {
    Write-Host "Node.js is already installed!" -ForegroundColor Green
    node --version
} else {
    Write-Host "Node.js not found. Downloading and installing..." -ForegroundColor Yellow
    
    # Create temp directory
    $tempDir = "$env:TEMP\node_installer"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    }
    
    # Download Node.js installer
    $url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
    $output = "$tempDir\node-installer.msi"
    
    Write-Host "Downloading Node.js 20.11.0 LTS..." -ForegroundColor Cyan
    Write-Host "(This may take a minute depending on your internet speed)" -ForegroundColor Gray
    Write-Host ""
    
    if (Download-WithProgress -Url $url -Output $output) {
        Write-Host "Download complete!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to download Node.js installer" -ForegroundColor Red
        Write-Host "Please install manually from: https://nodejs.org/" -ForegroundColor Red
        exit 1
    }
    
    # Install Node.js silently
    Write-Host "Installing Node.js (this may take a few minutes)..." -ForegroundColor Yellow
    $process = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $output, "/quiet", "/qn" -Wait -PassThru
    
    # Cleanup
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (Get-Command node -ErrorAction SilentlyContinue) {
        Write-Host "Node.js installed successfully!" -ForegroundColor Green
        node --version
    } else {
        Write-Host "WARNING: Node.js installation may have failed" -ForegroundColor Red
        Write-Host "Please install manually from: https://nodejs.org/" -ForegroundColor Red
        exit 1
    }
}

Write-Step "Setup Complete!"
Write-Host "You can now run start.bat to start the application" -ForegroundColor Green
Write-Host ""
