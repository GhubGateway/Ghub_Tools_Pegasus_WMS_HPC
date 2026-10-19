#--------------------------------------------------------------------------------
# receive_lunch_items.r
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: RLaunch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.a input file and the f.b output file

main <- function(argv) {
  
  username <- argv[1]
  
  # f.a contains the received lunch items
  
  fp1 <- file('f.a', 'r')
  fp2 <- file('f.b', 'w')
  
  lunch_items <- readLines(fp1, n=1)
  writeLines(sprintf('Hello %s! Received lunch items: %s.', username, lunch_items), fp2)
  
  close(fp1)
  close(fp2)
  
  # f.b contains the served lunch items
}

# Execute main function
main(commandArgs(trailingOnly = TRUE))
