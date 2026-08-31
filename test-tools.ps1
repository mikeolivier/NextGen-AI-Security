function Show-AgentResponse {
    param(
        [string]$File
    )

    $outer = Get-Content $File -Raw | ConvertFrom-Json
    $outer.body | ConvertFrom-Json | Format-List
}
