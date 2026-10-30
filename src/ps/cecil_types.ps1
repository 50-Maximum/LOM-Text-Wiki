param([string]$Dll = "E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\Managed\Mortal.Free.dll",
      [string]$Filter = "Event|Position|Requirement|Mission|Trigger|Cond")
$ErrorActionPreference = "Stop"
$cecil = "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
Add-Type -Path $cecil
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
Write-Output ("程序集: " + $asm.Name.Name + "  类型数: " + $asm.MainModule.Types.Count)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -match $Filter) {
    Write-Output ("`n== " + $t.FullName + "  [" + $t.Methods.Count + " 方法 / " + $t.Fields.Count + " 字段]")
    foreach ($f in $t.Fields) { if (-not $f.IsPrivate -or $f.FieldType.Name -match "List|Dictionary|Array") { Write-Output ("   字段 " + $f.FieldType.Name + " " + $f.Name) } }
    foreach ($m in $t.Methods) { Write-Output ("   方法 " + $m.Name + "(" + (($m.Parameters | ForEach-Object { $_.ParameterType.Name }) -join ", ") + ")") }
  }
}
