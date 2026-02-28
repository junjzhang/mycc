# Smart Pull Request

I'll create a pull request from your current branch to the target branch, analyzing changes and using your PR templates.

Arguments: `$ARGUMENTS` - The target branch name.

**What I'll do:**
- Analyze changes between current branch and target branch
- Use PR templates if available in `.github/` directory
- Search for related issues using `gh` CLI
- Auto-link and close relevant issues
- Create a comprehensive PR with proper formatting

First, let me verify the environment and gather information:

```bash
# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
TARGET_BRANCH="$ARGUMENTS"

if [ -z "$TARGET_BRANCH" ]; then
    echo "Error: Target branch not specified"
    echo "Usage: Provide target branch name as argument"
    exit 1
fi

echo "Current branch: $CURRENT_BRANCH"
echo "Target branch: $TARGET_BRANCH"

# Check if target branch exists
if ! git show-ref --verify --quiet refs/heads/$TARGET_BRANCH && ! git show-ref --verify --quiet refs/remotes/origin/$TARGET_BRANCH; then
    echo "Error: Target branch '$TARGET_BRANCH' does not exist"
    exit 1
fi
```

Now I'll analyze the changes and prepare the PR:

```bash
# Ensure we have the latest changes
git fetch origin

# Check if there are differences
if git diff --quiet origin/$TARGET_BRANCH..HEAD; then
    echo "No differences found between $CURRENT_BRANCH and $TARGET_BRANCH"
    exit 0
fi

# Show changes summary
echo "Changes to be included in PR:"
git diff --stat origin/$TARGET_BRANCH..HEAD
echo ""
git log --oneline origin/$TARGET_BRANCH..HEAD
```

I'll check for PR templates in your repository:

```bash
# Look for PR templates
PR_TEMPLATE=""
TEMPLATE_PATHS=(
    ".github/PULL_REQUEST_TEMPLATE.md"
    ".github/pull_request_template.md"
    ".github/PULL_REQUEST_TEMPLATE"
    ".github/PULL_REQUEST_TEMPLATE.txt"
    "docs/PULL_REQUEST_TEMPLATE.md"
    "PULL_REQUEST_TEMPLATE.md"
)

for template_path in "${TEMPLATE_PATHS[@]}"; do
    if [ -f "$template_path" ]; then
        PR_TEMPLATE="$template_path"
        echo "Found PR template: $template_path"
        break
    fi
done

if [ -n "$PR_TEMPLATE" ]; then
    echo "Using PR template from: $PR_TEMPLATE"
else
    echo "No PR template found"
fi
```

Now I'll analyze the changes to determine the PR type and scope:

```bash
# Analyze changed files
CHANGED_FILES=$(git diff --name-only origin/$TARGET_BRANCH..HEAD)
echo "Changed files:"
echo "$CHANGED_FILES"

# Determine change type based on files and commit messages
COMMIT_MESSAGES=$(git log --pretty=format:"%s" origin/$TARGET_BRANCH..HEAD)
```

Based on my analysis, I'll search for related issues:

```bash
# Extract potential issue numbers from commit messages and branch name
ISSUE_NUMBERS=$(echo "$COMMIT_MESSAGES $CURRENT_BRANCH" | grep -oE '#[0-9]+|[Ii]ssue[s]?\s*#?[0-9]+|[Ff]ix[es]*\s*#?[0-9]+|[Cc]lose[s]?\s*#?[0-9]+' | grep -oE '[0-9]+' | sort -u)

RELATED_ISSUES=""
CLOSES_ISSUES=""

if [ -n "$ISSUE_NUMBERS" ]; then
    echo "Checking for related issues..."
    for issue_num in $ISSUE_NUMBERS; do
        if gh issue view $issue_num &> /dev/null; then
            ISSUE_TITLE=$(gh issue view $issue_num --json title --jq '.title')
            echo "Found related issue #$issue_num: $ISSUE_TITLE"
            
            # Check if this should close the issue based on keywords
            if echo "$COMMIT_MESSAGES $CURRENT_BRANCH" | grep -iqE "(fix|close|resolve).*#?$issue_num|#$issue_num.*(fix|close|resolve)"; then
                CLOSES_ISSUES="$CLOSES_ISSUES\nCloses #$issue_num"
            else
                RELATED_ISSUES="$RELATED_ISSUES\nRelated to #$issue_num"
            fi
        fi
    done
fi
```

Now I'll create the PR title and body:

```bash
# Generate PR title based on changes
if echo "$COMMIT_MESSAGES" | grep -q "^feat\|^fix\|^docs\|^style\|^refactor\|^test\|^chore"; then
    # Use the most recent conventional commit as title
    PR_TITLE=$(echo "$COMMIT_MESSAGES" | head -n 1)
else
    # Generate title based on branch name and changes
    CLEAN_BRANCH=$(echo "$CURRENT_BRANCH" | sed 's/[_-]/ /g' | sed 's/\b\w/\U&/g')
    PR_TITLE="$CLEAN_BRANCH"
fi

# Build PR body
PR_BODY=""

if [ -n "$PR_TEMPLATE" ]; then
    PR_BODY=$(cat "$PR_TEMPLATE")
else
    # Create a basic PR body
    PR_BODY="## Changes
$(git log --pretty=format:"- %s" origin/$TARGET_BRANCH..HEAD)

## Files Changed
$(echo "$CHANGED_FILES" | sed 's/^/- /')
"
fi

# Add issue references
if [ -n "$CLOSES_ISSUES" ]; then
    PR_BODY="$PR_BODY

## Issues
$CLOSES_ISSUES"
fi

if [ -n "$RELATED_ISSUES" ]; then
    PR_BODY="$PR_BODY
$RELATED_ISSUES"
fi
```

Finally, I'll create the pull request:

```bash
# Push current branch to remote if needed
if ! git show-ref --verify --quiet refs/remotes/origin/$CURRENT_BRANCH; then
    echo "Pushing branch to remote..."
    git push -u origin $CURRENT_BRANCH
fi

# Create the PR
echo "Creating pull request..."
PR_URL=$(gh pr create \
    --title "$PR_TITLE" \
    --body "$PR_BODY" \
    --base "$TARGET_BRANCH" \
    --head "$CURRENT_BRANCH")

if [ $? -eq 0 ]; then
    echo "✅ Pull request created successfully!"
    echo "PR URL: $PR_URL"
    
    # Open PR in browser (optional)
    read -p "Open PR in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr view --web
    fi
else
    echo "❌ Failed to create pull request"
    exit 1
fi
```

**Important Notes:**
- I will NEVER add Claude signatures or AI attribution to PRs
- All PR content uses your existing git/GitHub configuration
- Issue linking follows GitHub's automatic closing keywords
- PR templates are used exactly as you've configured them
- The PR maintains full authenticity as your work