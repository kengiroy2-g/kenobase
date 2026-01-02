Set-Location 'C:\Users\kenfu\Documents\keno_base'
 = 'C:\Users\kenfu\Documents\keno_base'
 = 'HOUSE-003'
 = 'EXECUTOR'
 = 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\MEMORY\TASK_HOUSE-003_WORKING_SET.json'
 = '0'
 = '800000'
 = 'current_status;knowledgebase;CLAUDE.md'
 = 'AI_COLLABORATION/MESSAGE_QUEUE;AI_COLLABORATION/LOCKS'
$out = Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki2_EXECUTOR_20251228_204605.md' | & 'C:\Users\kenfu\.local\bin\claude.exe' --print --model opus  --dangerously-skip-permissions --tools Read,Edit,Write,Bash 
$out | Set-Content -Path 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-003_EXECUTOR_20251228_204605.md' -Encoding UTF8
$out
exit 
