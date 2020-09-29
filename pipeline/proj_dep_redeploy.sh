echo "------------------------ [ Dependant ReDeploy ]" 
deploy_launch=${DEPLOY_LAUNCH:-0}
bb_token=${bb_token:-$(getToken)}
redeployrepo="${BB_API}/${BITBUCKET_REPO_OWNER}/mstrade-api"

declare -a cmds=()

[[ $deploy_launch -eq 1 ]] && cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\": {\"type\": \"pipeline_pullrequest_target\"},\"selector\": {\"type\": \"pull-requests\",\"pattern\": \"**\"}}' \"${redeployrepo}/pipelines/\"")

runCommands "${cmds[@]}"
unset cmds
#-----
