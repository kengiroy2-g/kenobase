Set-Location 'C:\Users\kenfu\Documents\keno_base'
 = 'C:\Users\kenfu\Documents\keno_base'
 = 'EJ-001'
 = 'EXECUTOR'
 = 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\MEMORY\TASK_EJ-001_WORKING_SET.json'
 = '0'
 = '800000'
 = 'current_status;knowledgebase;CLAUDE.md'
 = 'AI_COLLABORATION/MESSAGE_QUEUE;AI_COLLABORATION/LOCKS'
$out = Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki6_EXECUTOR_20251230_054652.md' | & 'C:\Users\kenfu\.local\bin\claude.exe' --print --model opus  --dangerously-skip-permissions --tools Read,Edit,Write,Bash 
$out | Set-Content -Path 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_EJ-001_EXECUTOR_20251230_054652.md' -Encoding UTF8
$out
exit 
