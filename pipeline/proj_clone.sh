echo "------------------------ [ Updating Repositary ]"
declare -a gitCommands=()
if [[ -d '.git' ]]; then
 [[ -f '.git/MERGE_HEAD' ]] && gitCommands+=("git merge --abort")
 gitCommands+=("rm -f ./package-lock.json" "git checkout master" "git pull")
else
 gitCommands+=("git init" "git remote add origin $BITBUCKET_GIT_SSH_ORIGIN" "git fetch"  "git checkout master")
fi
runCommands "${gitCommands[@]}"
unset gitCommands
#-----

