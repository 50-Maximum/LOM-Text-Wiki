param([string]$Dll = "E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\LOMAssistant.dll",
      [string]$Out = "D:\LegendOfMortal Wiki\data\mod_res")
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
$res = $asm.MainModule.Resources
Write-Output ("资源数: " + $res.Count)
New-Item -ItemType Directory -Force -Path $Out | Out-Null
foreach ($r in $res) {
  $len = ""
  if ($r -is [Mono.Cecil.EmbeddedResource]) { $len = $r.GetResourceData().Length }
  Write-Output ("  " + $r.Name + "  [" + $r.ResourceType + "] " + $len)
  if ($r -is [Mono.Cecil.EmbeddedResource]) {
    $safe = $r.Name -replace '[\\/:*?"<>|]', '_'
    [System.IO.File]::WriteAllBytes((Join-Path $Out $safe), $r.GetResourceData())
  }
}
