# PowerShell script to push to GitHub
# Usage: .\push_to_github.ps1 -GitHubUsername "your-username" -RepoName "your-repo-name"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoName
)

Write-Host "🚀 Setting up GitHub remote..." -ForegroundColor Cyan

# Remove existing origin if it exists
git remote remove origin 2>$null

# Add new remote
$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
git remote add origin $remoteUrl

Write-Host "✓ Remote added: $remoteUrl" -ForegroundColor Green

# Rename branch to main if needed
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
    Write-Host "✓ Renamed branch to 'main'" -ForegroundColor Green
}

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "🌐 Repository URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to push. Make sure:" -ForegroundColor Red
    Write-Host "   1. The repository exists on GitHub" -ForegroundColor Yellow
    Write-Host "   2. You have push access" -ForegroundColor Yellow
    Write-Host "   3. You're authenticated (use: git config --global credential.helper wincred)" -ForegroundColor Yellow
}

