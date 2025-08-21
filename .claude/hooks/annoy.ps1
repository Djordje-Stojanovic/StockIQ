# Claude's Classy Notification System
# A sophisticated way to get your attention without being obnoxious

# Read hook input (in case we want to use it later)
$stdin = [Console]::In.ReadToEnd()

# Play a pleasant notification sound using Windows system sounds
# These are much nicer than harsh beeps
[System.Media.SystemSounds]::Exclamation.Play()

# Brief pause, then a second softer sound
Start-Sleep -Milliseconds 200
[System.Media.SystemSounds]::Question.Play()

# Gentle taskbar notification (just 3 flashes, not 15)
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool FlashWindow(IntPtr hWnd, bool bInvert);
    [DllImport("kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();
}
"@

$hwnd = [Win32]::GetConsoleWindow()
for($i=0; $i -lt 3; $i++) {
    [Win32]::FlashWindow($hwnd, $true)
    Start-Sleep -Milliseconds 200
}

# Optional: Windows 10/11 toast notification (uncomment if you want it)
# Add-Type -AssemblyName System.Windows.Forms
# [System.Windows.Forms.ToolTip]::new().Show("Claude finished!", "Notification", 3000)