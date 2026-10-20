## Git

show commit history:
```
git log
```

press `Enter` to continue further through the log and `q` to quit log.


```
git log --pretty=oneline
```

More options:

```
git log --pretty=oneline --max-count=2
git log --pretty=oneline --since='5 minutes ago'
git log --pretty=oneline --until='5 minutes ago'
git log --pretty=oneline --author=<your name>
git log --pretty=oneline --all
```

See `man git-log` for all details.


edit `.gitconfig` in the home directory:
```
[alias]
co = checkout
ci = commit
st = status
br = branch
hist = log --pretty=format:'%h %ad | %s%d [%an]' --graph --date=short
type = cat-file -t
dump = cat-file -p
```
