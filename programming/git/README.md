
# Resources:

## git online course
notes of git course on data camp：https://app.datacamp.com/learn/courses/introduction-to-git

## git guide:
https://rogerdudler.github.io/git-guide/

## book:
https://git-scm.com/book/en/v2

Git has three main states that your files can reside in: modified, staged, and committed:
- Modified: the file is changed but not committed to your database yet.
- Staged: you have marked a modified file in its current version to go into your next commit snapshot.
- Committed: the data is safely stored in your local database.


`git diff`: compares the working directory (Modified) with the staging area (Staged).

`git diff --staged`: compares your staged changes to your last commit.

`git commit -a -m 'Add new benchmarks'`: commit without adding files to the staging area.

`git rm <file>`: remove the file from the working directory. You will be able to commit this change. If you run `rm <file>`, the change is not added to the staging area.

`git rm -f <file>`: remove the modified file or file in the staging area.

`git rm --cached <file>`: remove files from the staging area but keep them in the working directory (hard drive).

`git mv <file1> <file2>`: rename <file1> to <file2>

`git log --pretty=format:"%h %s" --graph`: show commit history.

`git log -S <function_name>`: show commits that changed <function_name>.

`git log -- <path/to/file>`: show commits that changed the file.

### undo changes:

`git commit --amend`: commit files in the staging area and overwrite the last commit message.
> Only amend commits that are still local and have not been pushed somewhere.

`git reset HEAD <file_name>`: discard changes added to the staging area.

`git restore --staged <file_name>`: discard changes added to the staging area with git >= 2.23.0

`git checkout -- <file_name>`: discard changes in the modified file.

`git restore <file_name>`: discard changes in the modified file with git >= 2.23.0.

> `git checkout -- <file>` is a dangerous command. Any local changes you made to that file are gone — Git just replaced that file with the last staged or committed version.

> Anything that is committed in Git can almost always be recovered. Even commits that were on branches that were deleted or commits that were overwritten with an --amend commit.

### working with remotes:

> A repository can have multiple remotes, the default one is named `origin`.
> It is possible that you can be working with a “remote” repository that is, in fact, on the same host you are.

`git remote -v`: check the remote repositories configured in the current repo.

`git fetch <remote_repo>`: fetch all branches from the remote branch (default is `origin`)

`git pull`: fetch the remote branch (tracked by the local branch) and merge it into the local branch.
>If you want to rebase when pulling: git config --global pull.rebase "true", otherwise, it will merge if fast-forward is not possible.

`git push origin <branch_name>`: push commits in the local branch to the remote branch.

`git remote show origin>`: show information of the remote repository named origin (default).

`git remote rename pb paul`: rename remote repo pb to paul.

### Taggin:

`git tag -a v1.4 -m "my version 1.4"`: create an annotated tag.

`git show v1.4`: show tag information.

`git tag v1.4-lw`: create a light-weighted tag.

`git tag -a v1.2 <hash_tag>`: use commit with hash_tag to create tag.

`git push origin <tag_name>`: push tag to remote repo.

`git push origin --tags`: push all tags to the remote repo.

### set alias:

```
$ git config --global alias.co checkout
$ git config --global alias.br branch
$ git config --global alias.ci commit
$ git config --global alias.st status
```

## Git branching:

data stored in a git repository:

- blobs: stores the current version of each file when they are added to the staging area
- tree object: stores the directory information when changes are committed
- commit object: metadata and pointer to the root project tree.

The next commit stores a pointer to the commit that came immediately before it. A branch in Git is simply a lightweight movable pointer to one of these commits.

HEAD: (branch pointer) a special pointer to determine which branch you are currently on.

`git branch <branch_name>`: create a new branch.

`git log --oneline --decorate`: check which branch HEAD is pointed.
> git log will only show commit history below the branch you’ve checked out. To show all branches, use: `git log --all`

`git checkout <branch_name>`: switch to branch.

> A branch in Git is a simple file that contains the 40-character SHA-1 checksum of the commit it points to.

- fast-forward merge
- three-way merge
- merge commit: this is created in a three-way merge.


### manage branches:

`git branch -v`: see the last commit in each branch.

`git branch --merged`

`git branch --no-merged`

`git branch --move bad-branch-name corrected-branch-name`: rename branch locally.

`git push --set-upstream origin corrected-branch-name`: push renamed branch to remotes.

`git push origin --delete bad-branch-name`: delete the remote branch with the old name.

### branch workflow:

- long-running branch: You can have several branches that are always open and that you use for different stages of your development cycle.
- topic branch: a short-lived branch that you create and use for a particular feature or related work.

