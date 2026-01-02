Set-Location 'C:\Users\kenfu\Documents\keno_base'
 = 'C:\Users\kenfu\Documents\keno_base'
 = 'HOUSE-003'
 = 'VALIDATOR'
 = 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\MEMORY\TASK_HOUSE-003_WORKING_SET.json'
 = '1'
 = '200000'
 = 'current_status;knowledgebase;CLAUDE.md'
 = 'AI_COLLABORATION/MESSAGE_QUEUE;AI_COLLABORATION/LOCKS'
$out = Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki3_VALIDATOR_20251228_205205.md' | & 'C:\Users\kenfu\.local\bin\claude.exe' --print --model opus  --dangerously-skip-permissions --tools Read,Glob,Grep,Bash 
$out | Set-Content -Path 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HOUSE-003_VALIDATOR_20251228_205205.md' -Encoding UTF8
$out
exit 
