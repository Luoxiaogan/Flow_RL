# PowerShell脚本：批量移除被跟踪但在.gitignore中的文件

Write-Host "正在扫描被跟踪但在.gitignore中的文件..." -ForegroundColor Green

# 获取所有被跟踪的文件
$trackedFiles = git ls-files

if (-not $trackedFiles) {
    Write-Host "没有找到被跟踪的文件" -ForegroundColor Yellow
    exit
}

# 找出被忽略的文件
$ignoredTrackedFiles = @()
foreach ($file in $trackedFiles) {
    if (git check-ignore $file) {
        $ignoredTrackedFiles += $file
    }
}

if (-not $ignoredTrackedFiles) {
    Write-Host "没有找到被跟踪但在.gitignore中的文件" -ForegroundColor Yellow
    exit
}

Write-Host "`n找到 $($ignoredTrackedFiles.Count) 个被跟踪但在.gitignore中的文件:" -ForegroundColor Cyan
Write-Host ("-" * 80)

# 显示文件列表
for ($i = 0; $i -lt $ignoredTrackedFiles.Count; $i++) {
    $file = $ignoredTrackedFiles[$i]
    $size = if (Test-Path $file) { [math]::Round((Get-Item $file).Length / 1MB, 2) } else { 0 }
    Write-Host "$($i+1): $file ($size MB)" -ForegroundColor White
}

Write-Host ("-" * 80)

# 询问用户是否继续
$response = Read-Host "`n是否要从Git跟踪中移除这些文件? (y/N)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit
}

# 批量移除
Write-Host "`n正在从Git跟踪中移除文件..." -ForegroundColor Green
$removedCount = 0

foreach ($file in $ignoredTrackedFiles) {
    try {
        git rm --cached $file
        Write-Host "✓ 已移除: $file" -ForegroundColor Green
        $removedCount++
    }
    catch {
        Write-Host "✗ 移除失败: $file" -ForegroundColor Red
    }
}

Write-Host "`n完成! 已移除 $removedCount/$($ignoredTrackedFiles.Count) 个文件" -ForegroundColor Cyan

if ($removedCount -gt 0) {
    Write-Host "`n请运行以下命令提交更改:" -ForegroundColor Yellow
    Write-Host "git add ." -ForegroundColor White
    Write-Host "git commit -m 'Remove tracked files that should be ignored'" -ForegroundColor White
} 