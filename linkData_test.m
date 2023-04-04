clear all;
close all;

% Generate some data for a sample of 10 seconds
data_time = 25;
x = linspace(1, data_time);
y = zeros(1, 100);
y(1:100) = NaN;

% Create a figure and plot the data
figure;
plot(x, y)
ylim([0, 1024]) 

% Create a linkdata object for the figure
linkdata on
segment = 0;

while segment ~= 100
    y = update_y(y, segment);
    refreshdata
    segment  = segment + 1;
    pause(0.1)
end

function y = update_y(y, segment)
    % y((segment*10 + 1):(segment*10+10)) = randi(1025, 1, 10) - 1;
    y(segment+1) = randi(1025, 1) - 1; 
end


