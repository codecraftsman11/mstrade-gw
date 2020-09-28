echo "------------------------ [ Pre Deploy ]" 
deploy_launch=${DEPLOY_LAUNCH:-0}
bb_token=${bb_token:-$(getToken)}
deployrepo="${BB_API}/${BITBUCKET_REPO_OWNER}/${DEPLOY_REPO}"

declare -a cmds=()

[[ $deploy_launch -eq 1 ]] && cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\": {\"ref_type\": \"branch\",\"type\": \"pipeline_ref_target\", \"ref_name\": \"master\"}}' \"${deployrepo}/pipelines/\"")

runCommands "${cmds[@]}"
unset cmds

#-----
