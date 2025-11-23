%% Housing Macroeconomic Factors Analysis
clear; clc; close all;

%% 1. Setup and Load
inFile = 'Housing_Macroeconomic_Factors_US(good).xlsx'; 
outDir = 'output'; 
if ~exist(outDir, 'dir'), mkdir(outDir); end

try
    % readtable automatically detects headers like 'house_price_index'
    T = readtable(inFile);
    disp('✅ File loaded successfully.');
catch ME
    error('Could not read file. Make sure "%s" is in the current folder.', inFile);
end

%% 2. Data Setup
% Convert the 'Date' column to a MATLAB datetime format
if ismember('Date', T.Properties.VariableNames)
    % If it's not already a datetime, convert it
    if ~isdatetime(T.Date)
        T.Date = datetime(T.Date);
    end
else
    error('This file does not appear to have a "Date" column.');
end

% Sort by Date (important for line charts)
T = sortrows(T, 'Date');

%% 3. Plot 1: House Prices vs. Mortgage Rates (Dual Axis)
% We use 'yyaxis' to plot two different scales on the same chart
fig1 = figure('Name', 'Prices vs Rates', 'Position', [100 100 900 500]);
set(fig1, 'ToolBar', 'none'); % Prevent toolbar warning

yyaxis left
plot(T.Date, T.house_price_index, '-', 'LineWidth', 2);
ylabel('House Price Index (HPI)');
xlabel('Date');
% Set color manually if desired, or let MATLAB pick
ax = gca; ax.YColor = 'b'; 

yyaxis right
plot(T.Date, T.mortgage_rate, '-', 'LineWidth', 1.5);
ylabel('Mortgage Rate (%)');
ax.YAxis(2).Color = [0.85, 0.33, 0.1]; % Burnt Orange

title('US Housing Market: Prices vs. Mortgage Rates');
legend('House Price Index', 'Mortgage Rate', 'Location', 'best');
grid on;

saveas(fig1, fullfile(outDir, 'HPI_vs_Mortgage.png'));

%% 4. Plot 2: Economic Health (GDP & Employment)
fig2 = figure('Name', 'Economic Indicators', 'Position', [100 100 900 600]);
set(fig2, 'ToolBar', 'none');

% Top Subplot: GDP
subplot(2,1,1);
plot(T.Date, T.gdp, 'b-', 'LineWidth', 1.5);
title('GDP Growth Index');
ylabel('GDP');
grid on;

% Bottom Subplot: Employment Rate
subplot(2,1,2);
plot(T.Date, T.employment_rate, 'g-', 'LineWidth', 1.5);
title('Employment Rate (%)');
ylabel('Employment %');
xlabel('Date');
grid on;

saveas(fig2, fullfile(outDir, 'Economic_Health.png'));

disp('✅ Analysis complete. Graphs saved in "output" folder.');