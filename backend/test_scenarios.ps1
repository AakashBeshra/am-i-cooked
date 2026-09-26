$scenarios = @(
  "My exam is tomorrow and I haven't studied.",
  "I have a final exam in 3 hours and I know nothing.",
  "I have an exam next week and I've prepared a lot.",
  "I have 500 rupees left and payday is 20 days away.",
  "I spent all my money on a laptop and now I can't pay rent.",
  "My interview is in 2 hours and I just started learning Python.",
  "I told my boss to shut up in the meeting today.",
  "I accidentally texted my boss what I meant for my girlfriend.",
  "I slapped my principal.",
  "I got fired today.",
  "I'm just overthinking everything.",
  "My code doesn't compile and the deploy is in 30 minutes.",
  "I haven't started my final year project and it's due Friday.",
  "I broke up with my girlfriend yesterday and I regret it.",
  "I told three different people I'm free tonight."
)

$results = @()

foreach ($s in $scenarios) {
    $payload = @{ situation = $s; category = "auto" } | ConvertTo-Json
    try {
        $r = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/analyze" -ContentType "application/json" -Body $payload

        $src = "groq"
        if ($r.demo_mode) { $src = "rules" }

        Write-Host ""
        Write-Host ("-> " + $s) -ForegroundColor Cyan
        Write-Host ("   Score: " + $r.score + "  |  " + $r.severity + "  |  " + $r.category + "  |  source: " + $src)
        Write-Host ("   Diagnosis: " + $r.diagnosis)
        Write-Host ("   Plan[0]: " + $r.recovery_plan[0])
        Write-Host ("   Commentary: " + $r.funny_commentary)

        $row = New-Object PSObject -Property @{
            situation = $s
            score     = $r.score
            severity  = $r.severity
            category  = $r.category
            source    = $src
        }
        $results += $row
    } catch {
        Write-Host ("FAILED: " + $s + " -- " + $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Green
$results | Format-Table situation, score, severity, category, source -AutoSize
