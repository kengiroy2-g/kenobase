Set-Location 'C:\Users\kenfu\Documents\keno_base'
Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki0_PROXY_PLAN_20251230_033509.md' -Raw | & 'codex' exec --model gpt-5.1-codex-max -c model_reasoning_effort="high"  --dangerously-bypass-approvals-and-sandbox -o "C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-001_PROXY_PLAN_20251230_033509.md" -C 'C:\Users\kenfu\Documents\keno_base' -
exit 
