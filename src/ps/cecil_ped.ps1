param([string]$Dll = "E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\Managed\Mortal.Story.dll",
      [string]$Types = "PositionEventData|ConditionResult|StoryMapping|PositionEventRate")
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -match $Types) {
    Write-Output ("`n== " + $t.FullName + "  base=" + $t.BaseType.Name)
    foreach ($f in $t.Fields) {
      Write-Output ("   字段 [" + $f.FieldType.FullName + "] " + $f.Name)
    }
    foreach ($m in $t.Methods) {
      Write-Output ("   方法 " + $m.Name + "(" + (($m.Parameters | ForEach-Object { $_.ParameterType.Name }) -join ", ") + ")")
    }
  }
}
