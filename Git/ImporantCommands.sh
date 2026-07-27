# Remove all Local Branch Except "Main"
git branch | grep -v "main" | xargs git branch -D
