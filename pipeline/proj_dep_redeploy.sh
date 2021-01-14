echo "------------------------ [ Dependant ReDeploy ]" 
redeploy_launch=${REDEPLOY_LAUNCH:-0}
projectrepo="${BB_API}/${BITBUCKET_REPO_OWNER}"

declare -a cmds=()
if [ $redeploy_launch -eq 1 ]; then
 bb_token=${bb_token:-$(getToken)}
 for repo in ${REDEPLOY_REPOS[@]}; do 
  cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\":{\"type\":\"pipeline_ref_target\",\"ref_type\":\"branch\",\"ref_name\":\"master\",\"selector\":{\"type\":\"pull-requests\",\"pattern\":\"**\"}}}' \"${projectrepo}/${repo}/pipelines/\"")
 done 
fi
runCommands "${cmds[@]}"
unset cmds
#-----
