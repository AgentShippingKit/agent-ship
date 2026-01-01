# Open Source Branch Sync Strategy

## Problem Statement
Development has been done on the `main` branch (personal/HealthLogue-specific) instead of the `open-source` branch. We need to sync the open-source branch with generic improvements from main while excluding all HealthLogue-specific code.

## HealthLogue-Specific Content to Exclude

### 1. HealthLogue-Specific Agents

**Agents to EXCLUDE completely:**
- `src/agents/all_agents/medical_conversation_insights_agent/` - Medical conversation insights
- `src/agents/all_agents/medical_followup_agent/` - Medical followup questions

**Agents to RENAME and GENERALIZE for open-source:**
- `src/agents/all_agents/medical_reports_analysis_agent/` → `file_analysis_agent/` (generic file/document analysis)
- `src/agents/all_agents/health_assistant_agent/` → `personal_assistant_agent/` (simplified, generic assistant without HealthLogue-specific tools)

**Note:** The original HealthLogue-specific versions remain on `main` branch. Only the generalized versions go to `open-source`.

### 2. HealthLogue-Specific Tools
These tools should **NOT** be included:
- `src/agents/tools/conversation_insights_tool.py`
- `src/agents/tools/medical_reports_tool.py`
- `src/agents/tools/voice_notes_tool.py`
- `src/agents/tools/action_items_tool.py`
- `src/agents/tools/action_items_creation_tool.py`

### 3. HealthLogue References in Files
- `postman/AgentsAPI.postman_collection.json` - Contains "Healthlogue" references
- `postman/AgentAPI.postman_environment.json` - Contains "Healthlogue" references

### 4. Generic/Open-Source Content to Include
These should be included:
- Core framework improvements (base_agent, configs, modules, registry)
- Generic example agents: `orchestrator_pattern/`, `single_agent_pattern/`, `tool_pattern/`
- Debug UI (`debug_ui/`)
- Documentation improvements (`docs/`, `articles/`)
- Docker setup (`Dockerfile`, `docker-compose.yml`)
- Testing infrastructure (`tests/`)
- Build/deployment improvements (`Makefile`, `Procfile`)
- Configuration files (`.gitignore`, `env.example` - but review for HealthLogue refs)

## Recommended Strategy

### Option 1: Interactive Merge with Manual Filtering (Recommended for First Time)

This approach gives you full control and visibility:

1. **Create a temporary branch from open-source:**
   ```bash
   git checkout open-source
   git pull origin open-source
   git checkout -b open-source-sync
   ```

2. **Merge main into the temp branch:**
   ```bash
   git merge main --no-commit --no-ff
   ```

3. **Remove HealthLogue-specific content and generalize agents:**
   ```bash
   # Remove HealthLogue-specific agents (that can't be generalized)
   git rm -r src/agents/all_agents/medical_conversation_insights_agent/
   git rm -r src/agents/all_agents/medical_followup_agent/
   
   # Remove HealthLogue-specific tools
   git rm src/agents/tools/conversation_insights_tool.py
   git rm src/agents/tools/medical_reports_tool.py
   git rm src/agents/tools/voice_notes_tool.py
   git rm src/agents/tools/action_items_tool.py
   git rm src/agents/tools/action_items_creation_tool.py
   
   # Generalize and rename agents (run the generalization script)
   ./scripts/generalize_agents_for_opensource.sh
   ```
   
   The generalization script will:
   - Rename `medical_reports_analysis_agent` → `file_analysis_agent` (with generic content)
   - Create `personal_assistant_agent` from `health_assistant_agent` (simplified, without HealthLogue tools)
   - Update test files accordingly

4. **Clean up Postman files:**
   - Manually edit `postman/AgentsAPI.postman_collection.json` to remove "Healthlogue" references
   - Manually edit `postman/AgentAPI.postman_environment.json` to remove "Healthlogue" references
   - Or restore the open-source versions if they exist

5. **Review and clean up tool imports:**
   - Check `src/agents/tools/__init__.py` and remove HealthLogue-specific tool imports
   - Check any other files that import these tools

6. **Review environment variables:**
   - Check `env.example` for HealthLogue-specific variables (like `BACKEND_URL` if it's HealthLogue-specific)

7. **Commit the merge:**
   ```bash
   git commit -m "Sync open-source branch with main (excluding HealthLogue-specific content)"
   ```

8. **Test thoroughly:**
   ```bash
   # Run tests
   make test
   
   # Check that HealthLogue agents are not discoverable
   # Verify generic agents still work
   ```

9. **Merge to open-source:**
   ```bash
   git checkout open-source
   git merge open-source-sync
   git push origin open-source
   ```

### Option 2: Automated Script Approach

Use the provided `sync_open_source.sh` script (see below) to automate the process.

### Option 3: Cherry-Pick Specific Commits

If you want more granular control:

1. **Identify generic commits:**
   ```bash
   git log open-source..main --oneline
   ```

2. **Cherry-pick generic commits one by one:**
   ```bash
   git checkout open-source
   git cherry-pick <commit-hash>
   # Resolve conflicts and remove HealthLogue-specific content
   ```

This is more tedious but gives you commit-by-commit control.

## Going Forward: Best Practices

### 1. Development Workflow
- **For generic/framework improvements:** Work directly on `open-source` branch
- **For HealthLogue-specific features:** Work on `main` branch
- **For features that have both:** 
  - Develop generic parts on `open-source`
  - Develop HealthLogue-specific parts on `main`
  - Or use feature branches and merge appropriately

### 2. Branch Protection
- Consider protecting `open-source` branch to require PR reviews
- Use branch protection rules to prevent direct pushes

### 3. Regular Sync Schedule
- Sync `open-source` with `main` monthly or quarterly
- Document what was synced in a CHANGELOG

### 4. Code Organization
- Consider moving HealthLogue-specific agents to a separate directory structure
- Use feature flags or configuration to enable/disable HealthLogue features
- Keep HealthLogue-specific code clearly marked with comments

### 5. CI/CD Checks
- Add a pre-commit hook or CI check to scan for "HealthLogue" references in `open-source` branch
- Fail builds if HealthLogue-specific content is detected

## Verification Checklist

Before merging to open-source, verify:

- [ ] No HealthLogue-specific agents in `src/agents/all_agents/` (except generalized versions)
- [ ] `file_analysis_agent` exists (generalized from `medical_reports_analysis_agent`)
- [ ] `personal_assistant_agent` exists (simplified from `health_assistant_agent`)
- [ ] No HealthLogue-specific tools in `src/agents/tools/`
- [ ] No "Healthlogue" or "HealthLogue" references in code (except in comments explaining exclusion)
- [ ] Postman files use generic names
- [ ] Environment variables are generic
- [ ] All tests pass (including tests for generalized agents)
- [ ] Generic example agents (orchestrator, single_agent, tool_pattern) work correctly
- [ ] Generalized agents (`file_analysis_agent`, `personal_assistant_agent`) work correctly
- [ ] Documentation doesn't reference HealthLogue-specific features
- [ ] README is generic

## Files to Review Manually

These files may need manual review/editing:
- `postman/AgentsAPI.postman_collection.json`
- `postman/AgentAPI.postman_environment.json`
- `env.example` (check for HealthLogue-specific variables)
- `README.md` (ensure no HealthLogue references)
- `src/agents/tools/__init__.py` (remove HealthLogue tool imports)
- Any configuration files that might reference HealthLogue agents

## Recovery Plan

If you accidentally commit HealthLogue content to open-source:

1. **Immediate fix:**
   ```bash
   git checkout open-source
   git revert <commit-hash>
   ```

2. **Or rewrite history (if not pushed):**
   ```bash
   git rebase -i <commit-before-mistake>
   # Mark commits for editing and remove HealthLogue content
   ```

3. **If already pushed:**
   - Create a new commit removing the content
   - Consider using `git filter-branch` or `git filter-repo` for history rewriting (use with caution)

