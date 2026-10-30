param([string]$Types = "StoryMappingItem|ConditionResultItem|ConditionResult")
$ErrorActionPreference = "Continue"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$dir = "E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\Managed"
foreach ($p in Get-ChildItem $dir -Filter *.dll) {
  try { $asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($p.FullName) } catch { continue }
  $hit = $false
  foreach ($t in $asm.MainModule.Types) {
    if ($t.FullName -match $Types) {
      if (-not $hit) { Write-Output ("`n#### " + $p.Name); $hit = $true }
      Write-Output ("== " + $t.FullName + "  base=" + $t.BaseType.Name)
      foreach ($f in $t.Fields) { Write-Output ("   [" + $f.FieldType.FullName + "] " + $f.Name) }
    }
  }
}
