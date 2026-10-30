param([string]$Dll = "E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\LOMAssistant.dll",
      [string]$TypeFilter = "MapEventHints",
      [string]$MethodFilter = "LoadPositionEvents|GetPositionEvent|Events")
$ErrorActionPreference = "Stop"
Add-Type -Path "E:\Game\steamapps\common\LegendOfMortal\BepInEx\core\Mono.Cecil.dll"
$asm = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($Dll)
foreach ($t in $asm.MainModule.Types) {
  if ($t.FullName -notmatch $TypeFilter) { continue }
  Write-Output ("`n#### " + $t.FullName)
  foreach ($m in $t.Methods) {
    if ($m.Name -notmatch $MethodFilter) { continue }
    Write-Output ("`n  == " + $m.Name)
    if (-not $m.HasBody) { Write-Output "     (无方法体)"; continue }
    foreach ($ins in $m.Body.Instructions) {
      $op = $ins.OpCode.Name
      $arg = ""
      if ($ins.Operand -is [string]) { $arg = '"' + $ins.Operand + '"' }
      elseif ($ins.Operand -is [Mono.Cecil.MethodReference]) { $arg = $ins.Operand.DeclaringType.Name + "::" + $ins.Operand.Name }
      elseif ($ins.Operand -is [Mono.Cecil.FieldReference]) { $arg = $ins.Operand.DeclaringType.Name + "::" + $ins.Operand.Name }
      elseif ($null -ne $ins.Operand) { $arg = $ins.Operand.ToString() }
      if ($op -match "ldstr|call|callvirt|newobj|ldfld|stfld|ldsfld") { Write-Output ("     " + $op + " " + $arg) }
    }
  }
}
