param([string]$Dll, [string]$Types)
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -match $Types) {
    Write-Output ("== " + $t.FullName + "  base=" + $t.BaseType.Name)
    foreach ($f in $t.Fields) { Write-Output ("   [" + $f.FieldType.FullName + "] " + $f.Name) }
  }
}
