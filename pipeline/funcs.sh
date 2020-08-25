
runCommands() {
 cmds=("$@")
 GREEN='\033[0;32m'
 NC='\033[0m' # No Color
 for run_item in "${cmds[@]}"; do
  echo -e "${GREEN}Runing [ ${run_item} ] ...${NC}\n"
   ${run_item} || exit 1
 done
}
