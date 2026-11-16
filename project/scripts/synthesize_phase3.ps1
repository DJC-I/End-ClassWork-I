param([int]$Rate = 1)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$phase3Root = Split-Path $PSScriptRoot -Parent
$phase3Board = Get-Content -LiteralPath (Join-Path $phase3Root 'docs\phase3\storyboard.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$phase3Speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$phase3Speech.SelectVoice('Microsoft Huihui Desktop')
$phase3Speech.Rate = $Rate
$phase3Speech.Volume = 100
try {
  foreach ($phase3Video in $phase3Board.videos) {
    foreach ($phase3Scene in $phase3Video.scenes) {
      for ($phase3Index = 0; $phase3Index -lt $phase3Scene.lines.Count; $phase3Index++) {
        $phase3Name = '{0}_{1}_{2:00}.wav' -f $phase3Video.id, $phase3Scene.id, $phase3Index
        $phase3Wav = Join-Path $phase3Root ('.tools\phase3\speech\' + $phase3Name)
        $phase3Speech.SetOutputToWaveFile($phase3Wav, (New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(24000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)))
        $phase3Speech.Speak([string]$phase3Scene.lines[$phase3Index])
        $phase3Speech.SetOutputToNull()
      }
    }
    Write-Output ('Synthesized ' + $phase3Video.id)
  }
} finally { $phase3Speech.Dispose() }
