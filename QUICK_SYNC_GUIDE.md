# Quick Sync Guide - Open Source Branch

## TL;DR - Quick Steps

1. **Run the sync script:**
   ```bash
   ./scripts/sync_open_source.sh
   ```

2. **Manually clean up:**
   - Edit `postman/AgentsAPI.postman_collection.json` - remove "Healthlogue" references
   - Edit `postman/AgentAPI.postman_environment.json` - remove "Healthlogue" references  
   - Edit `src/agents/tools/__init__.py` - remove HealthLogue tool imports

3. **Verify no HealthLogue content:**
   ```bash
   ./scripts/check_healthlogue_refs.sh open-source-sync-YYYYMMDD-HHMMSS
   ```

4. **Test and commit:**
   ```bash
   make test
   git commit -m "Sync open-source with main (excluding HealthLogue content)"
   ```

5. **Merge to open-source:**
   ```bash
   git checkout open-source
   git merge open-source-sync-YYYYMMDD-HHMMSS
   git push origin open-source
   ```

## What Gets Excluded Automatically

✅ **Automatically handled by script:**
- **Removed:** `medical_conversation_insights_agent/`, `medical_followup_agent/`
- **Generalized & Renamed:** 
  - `medical_reports_analysis_agent/` → `file_analysis_agent/` (generic file analysis)
  - `health_assistant_agent/` → `personal_assistant_agent/` (simplified, generic assistant)
- **Removed:** All HealthLogue-specific tools (conversation_insights_tool, medical_reports_tool, voice_notes_tool, action_items_tool, action_items_creation_tool)

⚠️ **Requires manual cleanup:**
- Postman collection/environment files (HealthLogue references)
- `src/agents/tools/__init__.py` (tool imports)
- Any other files with "HealthLogue" text references

## Prevention for Future

Install pre-commit hook to prevent HealthLogue content in open-source:
```bash
cp scripts/pre-commit-hook-template.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Full Documentation

See `OPEN_SOURCE_SYNC_STRATEGY.md` for detailed strategy and best practices.

