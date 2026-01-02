Set-Location 'C:\Users\kenfu\Documents\keno_base'
Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki1_ARCHITECT_20251226_220222.md' -Raw | & 'codex' exec --model gpt-5.1-codex-max -c model_reasoning_effort="high"  --dangerously-bypass-approvals-and-sandbox -o "C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase4_task03_cli_ARCHITECT_20251226_220222.md" -C 'C:\Users\kenfu\Documents\keno_base' -
exit 
