echo "------------------------ [ Pre Deploy ]" 
deploy_launch=${DEPLOY_LAUNCH:-0}
bb_token=${bb_token:-$(getToken)}
deployrepo="${BB_API}/${BITBUCKET_REPO_OWNER}/${DEPLOY_REPO}"

declare -a cmds=()

[[ $deploy_launch -eq 1 ]] && cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\":{\"type\":\"pipeline_ref_target\",\"ref_type\":\"branch\",\"ref_name\":\"master\",\"selector\":{\"type\":\"pull-requests\",\"pattern\":\"**\"}}}'  \"${deployrepo}/pipelines/\"")

runCommands "${cmds[@]}"
unset cmds

#-----
