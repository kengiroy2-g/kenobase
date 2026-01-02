Set-Location 'C:\Users\kenfu\Documents\keno_base'
Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki0_PROXY_PLAN_20251230_193526.md' -Raw | & 'codex' exec --model gpt-5.1-codex-max -c model_reasoning_effort="high"  --dangerously-bypass-approvals-and-sandbox -o "C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_022_PROXY_PLAN_20251230_193526.md" -C 'C:\Users\kenfu\Documents\keno_base' -
exit 
