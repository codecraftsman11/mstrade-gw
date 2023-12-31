
runCommands() {
 cmds=("$@")
 GREEN='\033[0;32m'
 NC='\033[0m' # No Color
 for run_item in "${cmds[@]}"; do
  echo -e "\n${GREEN}Runing [ ${run_item} ] ...${NC}\n"
  eval "${run_item}" || exit 1
 done
}

getToken(){
 curl -s -X POST -u "${BB_KEY}:${BB_SECRET}" "https://bitbucket.org/site/oauth2/access_token" -d "grant_type=client_credentials" |jq -r 'to_entries[] | select( .key == ("access_token")) | ( "\(.value|tostring)")'
 [ $? -eq  0 ] || exit 1 
}
#-----

