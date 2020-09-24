echo "------------------------ [ Merge PR ]"
br_with_pq=${PROJ_BRANCH_TEST:-"test_master"}
wip_for_merge=${PROJ_WIP_MERGE:-"true"}

scmd="'pip install -q -r requirements.txt'"
[[ -z $(git branch | grep ${br_with_pq}) ]] \
 && swbranch="'git checkout -b ${br_with_pq}'" \
 || swbranch="'git checkout ${br_with_pq}'"

bb_token=${bb_token:-$(getToken)}
pr=$(curl -s -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${bb_token}" "$BB_API/${BITBUCKET_REPO_FULL_NAME}/pullrequests?state=OPEN&pagelen=50" | jq -r ".values[] | select( .title | test(\"^\\\s*wip:\"; \"ix\") | not or ${wip_for_merge} ) | (\"git pull --no-edit origin \\(.source.branch.name)\" | @sh)")

[[ $? -eq 0 ]] || return 1 

declare -a prarray="(${swbranch} ${pr} ${scmd})"
runCommands "${prarray[@]}"

[[ -z $pr ]] && exit 0
unset prarray
unset swbranch
#-----

