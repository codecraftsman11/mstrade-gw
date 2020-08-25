br_with_pq=${PROJ_BRANCH_TEST:-"test_master"}
declare -a gitCommands=()
[[ -f '.git/MERGE_HEAD' ]] && gitCommands+=("git merge --abort")
gitCommands+=("rm -f ./package-lock.json" "git checkout master")
[[ -z $(git branch | grep ${br_with_pq}) ]] || gitCommands+=("git branch -D ${br_with_pq}")

runCommands "${gitCommands[@]}"
unset gitCommands
#----- 
 
