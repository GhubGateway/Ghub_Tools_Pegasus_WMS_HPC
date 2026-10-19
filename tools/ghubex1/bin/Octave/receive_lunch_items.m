%--------------------------------------------------------------------------------
% receive_lunch_items.m
% Component of:
%     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
%     https://theghub.org/tools/ghubex1
% Compiled by: MATLAB_Build.sh and called by MATLAB_Launch.sh
% Also see Ghub, https://theghub.org/about
%--------------------------------------------------------------------------------

% In the Pegasus WMS YAML file,
% this job is specified to have the f.a input file and the f.b output file

function main(username)
    
    % f.a contains the received lunch items

    fp1 = fopen ('f.a', 'r');
    fp2 = fopen ('f.b', 'w');
 
    lunch_items = fgetl(fp1);
    fprintf (fp2, 'Hello %s! Received lunch items: %s.', username, lunch_items);

    fclose (fp1);
    fclose (fp2);

    % f.b contains the served lunch items

end
