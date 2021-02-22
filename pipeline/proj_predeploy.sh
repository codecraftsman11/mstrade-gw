echo "------------------------ [ Pre Deploy ]" 

deploy_launch=${DEPLOY_LAUNCH:-0}
bb_token=${bb_token:-$(getToken)}
deployrepo="${BB_API}/${BITBUCKET_REPO_OWNER}/${DEPLOY_REPO}"
cd ..

declare -a cmds=()
cmds+=("ln -sfn $(pwd)/${BITBUCKET_REPO_SLUG} ${HOME}/${BITBUCKET_REPO_SLUG}-ready"
      ) 

[[ $deploy_launch -eq 1 ]] && cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\":{\"type\":\"pipeline_ref_target\",\"ref_type\":\"branch\",\"ref_name\":\"master\",\"selector\":{\"type\":\"pull-requests\",\"pattern\":\"**\"}}}'  \"${deployrepo}/pipelines/\"")

v_uuid=$(curl -s -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${bb_token}"  "${deployrepo}/pipelines_config/variables/?pagelen=99" | jq -r ".values | .[] | select( .key == \"${DEPLOY_TAG:=BUILD_MASTER_TAG}\" ) | .uuid | @uri")

if [[ ! -z ${v_uuid} ]]; then
 cmds+=("curl -s -X DELETE -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" \"${deployrepo}/pipelines_config/variables/${v_uuid}\"")
fi

cmds+=("curl -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{ \"key\": \"${DEPLOY_TAG}\", \"value\": \"${git_tag}\", \"secured\": false}' \"${deployrepo}/pipelines_config/variables/\"")

runCommands "${cmds[@]}"
unset cmds

#-----
