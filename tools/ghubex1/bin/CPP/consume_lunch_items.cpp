//--------------------------------------------------------------------------------
// consume_lunch_items.cpp
// Component of:
//     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
//     https://theghub.org/tools/ghubex1
// Called from: C++_Launch.sh
// Also see Ghub, https://theghub.org/about
//--------------------------------------------------------------------------------

// In the Pegasus WMS YAML file,
// this job is specified to have the f.b input file and the f.c output file

#include <iostream>
#include <fstream>
#include <string>

int main(int argc, char *argv[]) {
    
    // f.b contains the served lunch items
    
    std::ifstream fp1("f.b");
    std::ofstream fp2("f.c");

    std::string served_lunch_items;
    if (std::getline(fp1, served_lunch_items)) {
        fp2 << served_lunch_items << " Thank you for lunch. Yum Yum!!";
    }

    fp1.close();
    fp2.close();

    // f.c contains the thank you note
    
    return 0;
}
