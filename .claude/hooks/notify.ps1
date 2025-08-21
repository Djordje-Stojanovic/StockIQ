# .claude\hooks\notify.ps1
$stdin = [Console]::In.ReadToEnd()
try { $data = $stdin | ConvertFrom-Json } catch { $data = $null }
$msg = if ($data -and $data.message) { $data.message } else { "Claude Code notification" }

# Beep and a Windows message box (no external modules)
[Console]::Beep(1000,300)
Add-Type -AssemblyName PresentationFramework
[System.Windows.MessageBox]::Show($msg, "Claude Code") | Out-Null