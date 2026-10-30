param([string]$Dll = "E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\Managed\Mortal.Core.dll",
      [string]$Types = "ConditionResultItem|StatCompareItem|StatValueReference|StatGroupVariable")
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -notmatch $Types) { continue }
  $attrs = ($t.CustomAttributes | ForEach-Object { $_.AttributeType.Name }) -join ","
  Write-Output ("`n== " + $t.FullName + "  base=" + $t.BaseType.Name + "  attrs=[" + $attrs + "]")
  foreach ($f in $t.Fields) {
    $fa = ($f.CustomAttributes | ForEach-Object { $_.AttributeType.Name }) -join ","
    $vis = if ($f.IsPublic) { "public" } elseif ($f.IsPrivate) { "private" } else { "other" }
    Write-Output ("   " + $vis + " [" + $f.FieldType.Name + "] " + $f.Name + "  attrs=[" + $fa + "]")
  }
}
