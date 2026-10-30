param([string]$Dll, [string]$Filter = "Event|Position|Mission|Condition|Trigger|Story|Free")
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
Write-Output ("程序集: " + $asm.Name.Name + " / 类型 " + $asm.MainModule.Types.Count)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -match $Filter) {
    Write-Output ("`n== " + $t.FullName)
    foreach ($f in $t.Fields) { Write-Output ("   字段 [" + $f.FieldType.Name + "] " + $f.Name) }
    foreach ($p in $t.Properties) { Write-Output ("   属性 " + $p.PropertyType.Name + " " + $p.Name) }
  }
}
