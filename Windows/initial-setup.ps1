# ==========================================
# Windows Fresh Install Automation Script
# ==========================================

Write-Host "Starting Windows Setup Script..." -ForegroundColor Cyan

# Ensure script is run with administrator privileges
If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Please run this script as an Administrator!"
    Break
}

# Array of apps to install via winget
$apps = @(
    # Browsers & Communication
    "Google.Chrome",
    "Mozilla.Firefox",
    "Discord.Discord",
    "Telegram.TelegramDesktop",
    
    # Utilities & Tools
    "7zip.7zip",
    "VideoLAN.VLC",
    "Microsoft.PowerToys",
    "Git.Git",
    
    # Development
    "Microsoft.VisualStudioCode",
    "OpenJS.NodeJS",
    "Python.Python.3.11",
    "Docker.DockerDesktop"
)

foreach ($app in $apps) {
    Write-Host "Installing $app..." -ForegroundColor Green
    winget install --id $app -e --accept-source-agreements --accept-package-agreements --silent
}

Write-Host "Setup completed successfully! Please restart your computer." -ForegroundColor Cyan
Pause
