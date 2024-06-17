# Checkout repository
# In local environment, you would manually clone the repository and navigate to it

# Set up Python
# Ensure that Python 3.11.4 is installed and added to PATH

# Install dependencies
# python -m pip install --upgrade pip
# pip install pyinstaller
# pip install -r requirements.txt

# Check if the directory exists and remove it
if (Test-Path -Path dist) {
    Remove-Item -Path dist -Recurse -Force
}
# Check if the directory exists and remove it
if (Test-Path -Path Output) {
    Remove-Item -Path Output -Recurse -Force
}
# Rest of your build script...

# Build with PyInstaller
pyinstaller --clean MorseCodeGUI.spec

# Download Inno Setup
# Ensure that Chocolatey is installed
# choco install innosetup --yes


$versionFile = "version"
$versionLine = Get-Content $versionFile | Select-Object -First 1
$versionNumber = $versionLine -replace "VersionNumber=", ""
[System.Environment]::SetEnvironmentVariable("APP_VERSION", $versionNumber, [System.EnvironmentVariableTarget]::Process)
Write-Output "APP_VERSION set to $versionNumber"
iscc MorseWriterInstaller.iss
        
# Build Installer
Start-Process -FilePath "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" -ArgumentList "MorseWriterInstaller.iss" -Wait

# Upload artifact
# In local environment, you would manually move the artifact to the desired location