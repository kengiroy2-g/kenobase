Set-Location 'C:\Users\kenfu\Documents\keno_base'
 = 'C:\Users\kenfu\Documents\keno_base'
 = 'HOUSE-002'
 = 'PROXY_IMPL'
 = 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\MEMORY\TASK_HOUSE-002_WORKING_SET.json'
 = '1'
 = '200000'
 = 'current_status;knowledgebase;CLAUDE.md'
 = 'AI_COLLABORATION/MESSAGE_QUEUE;AI_COLLABORATION/LOCKS'
$out = Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki0_PROXY_IMPL_20251228_203504.md' | & 'C:\Users\kenfu\.local\bin\claude.exe' --print --model opus  --dangerously-skip-permissions --tools Read,Glob,Grep,Bash 
$out | Set-Content -Path 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-002_PROXY_IMPL_20251228_203504.md' -Encoding UTF8
$out
exit 
