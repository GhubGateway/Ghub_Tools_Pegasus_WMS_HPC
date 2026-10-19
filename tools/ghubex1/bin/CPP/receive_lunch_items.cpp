//--------------------------------------------------------------------------------
// receive_lunch_items.cpp
// Component of:
//    https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
//     https://theghub.org/tools/ghubex1
// Called from: CPP_Launch.sh
// Also see Ghub, https://theghub.org/about
//--------------------------------------------------------------------------------

// In the Pegasus WMS YAML file,
// this job is specified to have the f.a input file and the f.b output file

#include <iostream>
#include <fstream>
#include <string>

int main(int argc, char *argv[]) {

    std::string username = argv[1];

    // f.a contains the received lunch items
    
    std::ifstream fp1("f.a");
    std::ofstream fp2("f.b");

    std::string lunch_items;
    if (std::getline(fp1, lunch_items)) {
        fp2 << "Hello " << username << "! Received lunch items: " << lunch_items << ".";
    }

    fp1.close();
    fp2.close();

    // f.b contains the served lunch items

    return 0;
}

