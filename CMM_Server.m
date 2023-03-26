clear all;
close all;

%% Setting things Up
% setting up mqtt client to thingspeak server
mqClient = mqttclient("tcp://mqtt3.thingspeak.com", 'Username', 'ETAANhkoAy4xJwcWHycSNy0', 'ClientID', 'ETAANhkoAy4xJwcWHycSNy0', 'Password', 'OnX0TX8k4mdNTqNDICP6JTNR', 'Port', 1883);

% confirminig client is connected
mqClient.Connected

% subscribing to read data from all fields
topicSub = "channels/2068835/subscribe/fields/+";
% QoS = 1 ensures message is received
Data = subscribe(mqClient, topicSub, 'QualityOfService', 1);

% time table to store all incoming subscription data
all_data = timetable();
% plotting 1 second of EMG data at a time
% data is received every second but there is 3 fields so the desired 
% amount of time in seconds to plot *3 is the num_data
sample_time = 1;
points_per_plot = 3*sample_time;
figure
linkdata on
num_responses = 0;

while true
    curr_data = get_data(points_per_plot, mqClient);
    num_responses = num_responses + 1;
    all_data = vertcat(all_data, curr_data);
    [emgArray, datetimeArray] = parse_data(all_data);
    size(all_data);
    plot_data(emgArray, datetimeArray, points_per_plot)
    pause(1)
end

%% Get Subscription Data
function data_table = get_data(num_points, mqClient)
    data_table = timetable();

    while size(data_table) < num_points
        % appending incoming data to all_data table
        data_table = vertcat(data_table, read(mqClient));
        size(data_table) % to watch data come in
    end
end

%% Prep data for plotting
function [emgArray, datetimeArray] = parse_data(data_table)
    [row, col] = size (data_table);
    % ccArray = str2double(field_data(1));
    emgArray = [];
    datetimeArray = [];
    field_data = data_table.Data;
    time_data = data_table.Time;

    for i = 1:row
        % Calculate indices for current set of values
        if mod(i,3) == 2
            data = str2num(cell2mat(field_data(i)));
            emgArray = [emgArray, data];
        elseif mod(i,3) == 0
            [yr, mon, day] = ymd(time_data(i));
            [hr, min, sec] = hms(time_data(i));
            if (~isempty(datetimeArray) && sec - second(datetimeArray(end)) > 1)
                    sec = second(datetimeArray(end)) + 1;
            end
            for ms = 0:100:900               
                d = datetime((yr), int8(mon), int8(day), int8(hr), int8(min), int8(sec), ms);
                datetimeArray = [datetimeArray, d];
            end
%             time_string = cell2mat(field_data(i));
%             time_string = strrep(time_string, "[", "");
%             time_string = strrep(time_string, "]", "");
%             time_string = strsplit(time_string, ", ");
%             time_string = erase(time_string, "'");
%             time_string = strtrim(time_string);
            datetimeArray.Format = 'yyyy-MM-dd HH:mm:ss.SS';
        end
    end
    emgArray = emgArray';
    datetimeArray = datetimeArray';
end

function plot_data(emgArray, datetimeArray, N) 
    linkdata on
    % plot(datetimeArray(end-N+1:end), emgArray(end-N+1:end));
    plot(datetimeArray, emgArray);
    ylim('padded');
    refreshdata;
end
