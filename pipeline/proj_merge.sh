echo "------------------------ [ Merge PR ]"
br_with_pq=${PROJ_BRANCH_TEST:-"test_master"}
wip_for_merge=${PROJ_WIP_MERGE:-"true"}

scmd="'rm -f ./package-lock.json'"
[[ -z $(git branch | grep ${br_with_pq}) ]] \
 && swbranch="'git checkout -b ${br_with_pq}'" \
 || swbranch="'git checkout ${br_with_pq}'"

pr=$(curl -s -u "${PROJ_UKEY}:${PROJ_PKEY}" "https://api.bitbucket.org/2.0/repositories/${BITBUCKET_REPO_FULL_NAME}/pullrequests?state=OPEN&pagelen=50" | jq -r ".values[] | select( .title | test(\"^\\\s*wip:\"; \"ix\") | not or ${wip_for_merge} ) | (\"git pull --no-edit origin \\(.source.branch.name)\" | @sh)")

[[ -z $pr ]] && exit 1

declare -a prarray="(${swbranch} ${scmd} ${pr})"
runCommands "${prarray[@]}"
unset prarray
unset swbranch
#-----

