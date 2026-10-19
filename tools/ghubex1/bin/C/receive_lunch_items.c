//--------------------------------------------------------------------------------
// receive_lunch_items.c
// Component of:
//    https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
//     https://theghub.org/tools/ghubex1
// Called from: C_Launch.sh
// Also see Ghub, https://theghub.org/about
//--------------------------------------------------------------------------------

// In the Pegasus WMS YAML file,
// this job is specified to have the f.a input file and the f.b output file

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    
    char *username = argv[1];

    // f.a contains the received lunch items
    
    FILE *fp1 = fopen("f.a", "r");
    FILE *fp2 = fopen("f.b", "w");

    char lunch_items[512];
    if (fgets(lunch_items, sizeof(lunch_items), fp1) != NULL) {
        // Remove trailing "\n" added by fgets
        lunch_items[strcspn(lunch_items, "\n")] = 0;
        fprintf(fp2, "Hello %s! Received lunch items: %s.", username, lunch_items);
    }

    fclose(fp1);
    fclose(fp2);

    // f.b contains the served lunch items

    return 0;
}

