# plague

Forked version of plague with ClearOS changes applied

## Update usage
  Add __#kojibuild__ to commit message to automatically build

* git clone git+ssh://git@github.com/clearos/plague.git
* cd plague
* git checkout master
* git remote add upstream git://pkgs.fedoraproject.org/plague.git
* git pull upstream master
* git checkout infra7
* git merge --no-commit master
* git commit
