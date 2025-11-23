%% Plot Homelessness Trends (2007-2024)
clear; clc; close all;

%% 1. Load Data
% The file you uploaded was converted to a CSV format
inFile = 'HomelessYears.xlsx';

if ~exist(inFile, 'file')
    error('File "%s" not found. Make sure it is in your MATLAB folder.', inFile);
end

% Read the table. 'VariableNamingRule', 'preserve' keeps "Overall Homeless"
% with the space, so we don't get messy variable names.
T = readtable(inFile, 'VariableNamingRule', 'preserve');

% Display first few rows to verify
disp('Data Preview:');
disp(head(T));

%% 2. Extract Variables
% We use T.("Name") to handle column names with spaces
years = T.year;
counts = T.("Overall Homeless");

%% 3. Create Plot
fig1 = figure('Name', 'Homelessness Trend', 'Position', [100, 100, 900, 600]);

% Plot line with markers
plot(years, counts, '-o', ...
    'LineWidth', 2.5, ...
    'MarkerSize', 8, ...
    'MarkerFaceColor', 'b', ...
    'Color', [0 0.447 0.741]); % Standard MATLAB Blue

%% 4. Format Graph
grid on;
title('Overall Homelessness in the US (2007-2024)', 'FontSize', 14);
xlabel('Year', 'FontSize', 12);
ylabel('Total Homeless Count', 'FontSize', 12);

% Format Y-axis to show actual numbers (no scientific notation)
ax = gca;
ax.YAxis.Exponent = 0; 
ytickformat('%,.0f'); % Adds commas to the numbers (e.g., 600,000)

% Set X-axis limits to match data
xlim([min(years)-1, max(years)+1]);
xticks(min(years):max(years)); % Show every year on the axis

% Add a text annotation for the 2021 dip (if it exists in data)
idx2021 = find(years == 2021);
if ~isempty(idx2021)
    text(2021, counts(idx2021), '  2021 Dip (Pandemic Data Issues)', ...
        'VerticalAlignment', 'bottom', 'FontSize', 10);
end

%% 5. Save Output
saveas(fig1, 'Homelessness_Trend_Graph.png');
disp('✅ Graph created and saved as "Homelessness_Trend_Graph.png"');