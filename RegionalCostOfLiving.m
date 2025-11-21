%% Regional Cost of Living Analysis
clear; clc; close all;

%% 1. Setup and Load
inFile = 'Regional Cost of Living.xlsx'; 
outDir = 'output'; 
if ~exist(outDir, 'dir'), mkdir(outDir); end

try
    T = readtable(inFile);
    disp('✅ File loaded successfully.');
catch ME
    error('Could not read file. Make sure "%s" is in your MATLAB folder.', inFile);
end

% Clean: Remove invalid years
if ismember('Year', T.Properties.VariableNames)
    T = T(T.Year > 1900, :); 
end

%% 2. Aggregate Data (FIXED)
% We list ONLY the numeric columns we want to average. 
% This prevents MATLAB from trying to average "Country" or "Region".
varsToAverage = {'Average_Monthly_Income', 'Cost_of_Living', ...
                 'Housing_Cost_Percentage', 'Tax_Rate', ...
                 'Healthcare_Cost_Percentage', 'Education_Cost_Percentage', ...
                 'Transportation_Cost_Percentage'};

% Calculate mean only for the variables listed above, grouped by Year
T_avg = groupsummary(T, 'Year', 'mean', varsToAverage);

disp('Data aggregated by Year.');

%% 3. Visualization 1: Income vs Cost
% Note: groupsummary adds 'mean_' to the column names
years = T_avg.Year;
income = T_avg.mean_Average_Monthly_Income;
cost   = T_avg.mean_Cost_of_Living;

fig1 = figure('Name', 'Income vs Cost', 'Position', [100 100 1000 600]);
set(fig1, 'ToolBar', 'none'); 

plot(years, income, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Monthly Income');
hold on;
plot(years, cost, '-x', 'LineWidth', 2, 'DisplayName', 'Cost of Living');
hold off;

grid on;
title('Average Trends: Income vs. Cost of Living');
xlabel('Year');
ylabel('Amount (USD)');
legend('Location', 'best');

saveas(fig1, fullfile(outDir, 'Income_vs_Cost_Trend.png'));

%% 4. Visualization 2: Percentage Breakdown Stacked
percentage_cols = [T_avg.mean_Housing_Cost_Percentage, T_avg.mean_Tax_Rate, ...
                   T_avg.mean_Healthcare_Cost_Percentage, T_avg.mean_Education_Cost_Percentage, ...
                   T_avg.mean_Transportation_Cost_Percentage];

legend_names = {'Housing', 'Tax', 'Healthcare', 'Education', 'Transportation'};

fig2 = figure('Name', 'Cost Breakdown', 'Position', [100 100 1000 600]);
set(fig2, 'ToolBar', 'none');

bar(years, percentage_cols, 'stacked');

grid on;
title('Average Cost of Living Breakdown by Year');
xlabel('Year');
ylabel('Percentage of Income (%)');
legend(legend_names, 'Location', 'eastoutside');

saveas(fig2, fullfile(outDir, 'Cost_Breakdown_Stacked.png'));

disp('✅ Analysis complete. Graphs saved in "output" folder.');