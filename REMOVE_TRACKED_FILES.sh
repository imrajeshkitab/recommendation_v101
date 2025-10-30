#!/bin/bash
#
# Script to remove tracked files that should now be ignored by .gitignore
# This will remove files from git tracking but keep them in your local filesystem
#
# Usage: bash REMOVE_TRACKED_FILES.sh
#

echo "=================================================="
echo "Removing tracked files from git (keeping locally)"
echo "=================================================="
echo ""

# Remove database files from git tracking
echo "🗃️  Removing database files from git..."
git rm --cached -r database/content/bytes/*.txt
git rm --cached -r database/content/journeys/*.txt
git rm --cached -r database/content/summaries/*.txt
git rm --cached -r database/tables/*.csv

# Remove outputs/script_outputs files from git tracking
echo "📤 Removing outputs/script_outputs files from git..."
git rm --cached -r outputs/script_outputs/tag_extractor_batch-bytes/*.json
git rm --cached -r outputs/script_outputs/tag_extractor_batch-journeys/*.json
git rm --cached -r outputs/script_outputs/tag_extractor_batch-summaries/*.json
git rm --cached -r outputs/other/* 2>/dev/null || true

# Remove archives files from git tracking
echo "📦 Removing archives files from git..."
git rm --cached -r archives/*.csv 2>/dev/null || true
git rm --cached -r archives/* 2>/dev/null || true

# Remove logs files from git tracking (if any)
echo "📝 Removing log files from git..."
git rm --cached -r logs/**/*.log 2>/dev/null || true

# Remove test/script_outputs files
echo "🧪 Removing test script outputs from git..."
git rm --cached -r test/script_outputs/extract_tags_with_gemini/*.json 2>/dev/null || true
git rm --cached -r test/script_outputs/tag_extractor/*.json 2>/dev/null || true

echo ""
echo "=================================================="
echo "✅ Done! Files removed from git tracking."
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "1. Review changes: git status"
echo "2. Commit the removal: git commit -m 'Remove data files from git tracking'"
echo "3. Push to remote: git push"
echo ""
echo "⚠️  Note: Files are still on your local filesystem"
echo "🔒 Future changes to these files won't be tracked by git"
echo ""

