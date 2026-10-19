//--------------------------------------------------------------------------------
// consume_lunch_items.c
// Component of:
//     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
//     https://theghub.org/tools/ghubex1
// Called from: C_Launch.sh
// Also see Ghub, https://theghub.org/about
//--------------------------------------------------------------------------------

// In the Pegasus WMS YAML file,
// this job is specified to have the f.b input file and the f.c output file

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    
    // f.b contains the served lunch items
    
    FILE *fp1 = fopen("f.b", "r");
    FILE *fp2 = fopen("f.c", "w");

    if (fp1 == NULL || fp2 == NULL) {
        perror("Error opening file");
        return EXIT_FAILURE;
    }

    char served_lunch_items[512];
    if (fgets(served_lunch_items, sizeof(served_lunch_items), fp1) != NULL) {
        // Remove trailing "\n" added by fgets
        served_lunch_items[strcspn(served_lunch_items, "\n")] = 0;
        fprintf(fp2, "%s Thank you for lunch. Yum Yum!!", served_lunch_items);
    }

    fclose(fp1);
    fclose(fp2);

    // f.c contains the thank you note
    
    return 0;
}

