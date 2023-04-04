function writeToCSV(all_data)

    % for each user you only have one file, add data to the bottom 
    %% Header Data
    % Sets the Day to today
    Date = string(datetime("today"));
    
    % Sets the user variable to invalid, will continue to ask user to enter
    % user until valid entrance is entered
    user = 'invalid';
    
    while strcmp(user,'invalid')
        
        % Prompt to specify the user of the device
        patient_number = input('Please enter the patient name: ','s');
    
        switch patient_number
            case 'Stefanie'
                user = patient_number;
            case 'Huzaifa'
                user = patient_number;
            case 'Mayuri'
                user = patient_number;
            case 'Zuzanna'
                user = patient_number;
            case 'exit'
                return
            otherwise
                errormsg = msgbox('User entry is not valid, please try again');
                user; 
        end
    end
    
    % Read data from file
    recieved_data = timetable2table(all_data);
    % Remove redundant data from table
    recieved_data = removevars(recieved_data,["Time","Topic"]);

    % REmove uneeded rows
    recieved_data(4:4:end,:) = [];

    % Initialize calf circumference table and change headings
    % This line takes the data at the first row and then every 4th row to
    % make a table of only CC
    calfcircumference = recieved_data(1:3:end,:);
    calfcircumference = renamevars(calfcircumference,["Data"],["Calf Circumference"]);
    
    % Get height of data to create that many rows w/ CC
    h = height(calfcircumference);
    sz = [h 2];
    
    % Initialize EMG Data table
    % This line takes the data at the second row and then every third row to
    % make a table of only EMG data
    EMG_data = recieved_data(2:3:end,:);
    EMG_data = renamevars(EMG_data,["Data"],["EMG Data"]);
    
    % Initialize output table
    EMG_data2 = table; 
    
    % Go through each row
    for i = 1:h
        x = (EMG_data(i,"EMG Data"));
        % Change format to array so we can extract data
        x = table2array(x);
        expression = ',';
        % Get seperates the voltage values into individual cells 
        y = regexp(x,expression,'split')';
        match = ["[","]"," "];
        % Removes unnecessary brackets and spaces
        y = erase(y,match);
        % Change back to table
        y = array2table(y);
        y = renamevars(y,["y"],["EMG Data"]);
        % Append this data to the output table
        EMG_data2 = [EMG_data2;y];
    end
    
    % Initialize timestamp table
    % This line takes the data at the third row and then every third row to
    % make a table of only timestamps
    timestamp = recieved_data(3:3:end,:);
    timestamp = renamevars(timestamp,["Data"],["Time(hh.mm.ss)"]);
    
    % Initialize output table
    timestamp2 = table; 
    
    % See comments for EMG Data
    % Yes technically I could have called a function but I was lazy and didnt
    % want to pass variables back and forth
    
    for i = 1:h
        x = (timestamp(i,"Time(hh.mm.ss)"));
        x = table2array(x);
        expression = ',';
        y = regexp(x,expression,'split')';
        match = ["[","]"," "];
        y = erase(y,match);
        y = array2table(y);
        y = renamevars(y,["y"],["Time(hh.mm.ss)"]);
        timestamp2 = y;
    end

    % This is the new table that will be used as output
    calfcircumference2 = table;
    
    h = height(EMG_data2);
    ccADC = (calfcircumference(i,"Calf Circumference"))
    ccADC = table2array(ccADC);
    dbl_array = zeros(1, length(ccADC));
    for i = 1:length(ccADC)
        dbl_array(i) = str2double(ccADC(i));
    end

    cc = 1.735561368915665e-05*(dbl_array)^2 - 0.076597226819869*(dbl_array) + 1.154162019528474e+02
%     k = (calfcircumference(i,"Calf Circumference"))
    a = repmat(cc,h,1);
    calfcircumference2 = array2table(a,'VariableNames',["Calf Circumference"]);
    
    % Rename table headers
    %calfcircumference2 = renamevars(calfcircumference2,["c"],["Calf Circumference"]);
    
    % This gets the length of the output tables and creates a column of the
    % same size containing the date
    a = repmat(Date,h,1);
    User_data = array2table(a,'VariableNames',["Date"]);
    
    % Joins all the tables together
    data = [User_data timestamp2 EMG_data2 calfcircumference2];
    
    % Dynamically name each file according to user, date, & time
    Filename = strcat("User ", string(user), ".xlsx");
    
    % Check if the user already has a file
if isfile(Filename)
        % File exists. Append data to file
        writetable(data, Filename,'WriteMode','append')
    else
        % User File does not exist. Create new file for user
        writetable(data,Filename)
end

