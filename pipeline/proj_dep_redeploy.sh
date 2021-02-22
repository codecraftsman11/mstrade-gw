echo "------------------------ [ Dependant ReDeploy ]" 
redeploy_launch=${REDEPLOY_LAUNCH:-0}
rmoldbuildfolder=${REDEPLOY_OLD_FOLDER_RM:-0}
projectrepo="${BB_API}/${BITBUCKET_REPO_OWNER}"
gittag=$(git describe --always --abbrev --tags --long)
createdate=$(date +%Y%m%d%H%M%S)
destfolder="${BITBUCKET_REPO_SLUG}---${gittag}-${createdate}"


cd ..
declare -a cmds=()
cmds+=("mkdir -p ${destfolder}"
       "cp -r ${BITBUCKET_REPO_SLUG}/mst_gateway ./${destfolder}/" 
       "ln -sfn $(pwd)/$destfolder ${HOME}/${BITBUCKET_REPO_SLUG}-ready"
      )

if [ $redeploy_launch -eq 1 ]; then
 bb_token=${bb_token:-$(getToken)}
 for repo in ${REDEPLOY_REPOS[@]}; do 
  cmds+=("curl --output /dev/null -s -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer ${bb_token}\" --data '{\"target\":{\"type\":\"pipeline_ref_target\",\"ref_type\":\"branch\",\"ref_name\":\"master\",\"selector\":{\"type\":\"pull-requests\",\"pattern\":\"**\"}}}' \"${projectrepo}/${repo}/pipelines/\"")
 done 
fi
[[ $rmoldbuildfolder -eq 1 ]] && cmds+=("find ./ -maxdepth 1 -type d \( -name \"${BITBUCKET_REPO_SLUG}---*\" -and -not -name \"${destfolder}\" \) -exec rm -r \"{}\" \;")

runCommands "${cmds[@]}"
unset cmds
#-----
