Set-Location 'C:\Users\kenfu\Documents\keno_base'
Get-Content 'C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\ARTIFACTS\v4_runtime\prompt_ki2_EXECUTOR_20251228_185152.md' -Raw | & 'codex' exec --model gpt-5.1-codex-max -c model_reasoning_effort="high"  --dangerously-bypass-approvals-and-sandbox -o "C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DOC-001_EXECUTOR_20251228_185152.md" -C 'C:\Users\kenfu\Documents\keno_base' -
exit 
