%% Housing Group 8 - Annual Macroeconomic Factors (Simple Analysis)
% Goal: Simple, readable analysis per professor's template
% Data: Annual_Macroeconomic_Factors.xlsx (sheet 'in')

clear; clc; close all;

%% 1) Load dataset (readtable)
file = 'Annual_Macroeconomic_Factors.xlsx';
sheet = 'in';
T = readtable(file, 'Sheet', sheet);

% Ensure Date is datetime
if ~isdatetime(T.Date)
    try
        T.Date = datetime(T.Date);
    catch
        T.Date = datetime(T.Date, 'InputFormat','yyyy-MM-dd'); % fallback
    end
end

%% 2) Handle missing/invalid values (simple + safe)
% Coerce numeric columns (ignore Date)
numVars = setdiff(T.Properties.VariableNames, {'Date'});
for i = 1:numel(numVars)
    % If a column is char/cellstr, convert to numeric (str2double)
    if iscell(T.(numVars{i})) || isstring(T.(numVars{i})) || ischar(T.(numVars{i}))
        T.(numVars{i}) = str2double(string(T.(numVars{i})));
    end
end

% Option A (strict, student-simple): drop rows that are entirely missing in numerics
allNumMissing = all(ismissing(T(:, numVars)), 2);
Tclean = T(~allNumMissing, :);

% (Your file has no missing values; these steps are just to match expectations.)

%% 3) Summary statistics (simple, per professor's list) for a few key variables
varsForStats = {'House_Price_Index','Mortgage_Rate','Unemployment_Rate', ...
                'Real_Disposable_Income','Real_GDP'};

fprintf('=== Summary Statistics (ignoring missing) ===\n');
for v = 1:numel(varsForStats)
    x = Tclean.(varsForStats{v});
    x = x(~isnan(x));
    if isempty(x), continue; end
    fprintf('\nVariable: %s\n', varsForStats{v});
    fprintf('  Count: %d\n', numel(x));
    fprintf('  Mean: %.4f\n', mean(x));
    fprintf('  Std:  %.4f\n', std(x));
    fprintf('  Min:  %.4f\n', min(x));
    fprintf('  Med:  %.4f\n', median(x));
    fprintf('  Max:  %.4f\n', max(x));
    fprintf('  Sum:  %.4f\n', sum(x));
end

%% 4) "Mostly sold item / payment method" analogues
% Not applicable for macro data. We'll instead compute simple decadal summaries.

% Add decade column
yr = year(Tclean.Date);
decade = floor(yr/10)*10;
Tclean.Decade = decade;

% Decadal averages for two intuitive metrics
decTbl = groupsummary(Tclean, "Decade", "mean", ["Mortgage_Rate","Unemployment_Rate"]);
decTbl.Properties.VariableNames = {'Decade','GroupCount','Avg_Mortgage_Rate','Avg_Unemployment_Rate'};

%% 5) Visuals (simple and clear)

% Line chart: main macro series over time (separate figures to keep it simple)
figure('Name','House Price Index');
plot(Tclean.Date, Tclean.House_Price_Index, 'LineWidth',1.5); grid on;
xlabel('Year'); ylabel('Index'); title('House Price Index over Time');

figure('Name','Mortgage Rate');
plot(Tclean.Date, Tclean.Mortgage_Rate, 'LineWidth',1.5); grid on;
xlabel('Year'); ylabel('Percent'); title('Mortgage Rate over Time');

figure('Name','Unemployment Rate');
plot(Tclean.Date, Tclean.Unemployment_Rate, 'LineWidth',1.5); grid on;
xlabel('Year'); ylabel('Percent'); title('Unemployment Rate over Time');

figure('Name','Real Disposable Income');
plot(Tclean.Date, Tclean.Real_Disposable_Income, 'LineWidth',1.5); grid on;
xlabel('Year'); ylabel('Dollars (real)'); title('Real Disposable Income over Time');

% Histogram of Mortgage Rate (like "Histogram of Total Spent" in the example)
figure('Name','Histogram - Mortgage Rate');
histogram(Tclean.Mortgage_Rate);
grid on; xlabel('Mortgage Rate (%)'); ylabel('Count');
title('Distribution of Mortgage Rates');

% Bar chart of decadal average Mortgage Rate (analogue to "Bar Chart per Item")
figure('Name','Bar - Avg Mortgage Rate by Decade');
bar(decTbl.Decade, decTbl.Avg_Mortgage_Rate);
grid on; xlabel('Decade'); ylabel('Avg Mortgage Rate (%)');
title('Average Mortgage Rate by Decade');

% Bar chart of decadal average Unemployment Rate
figure('Name','Bar - Avg Unemployment Rate by Decade');
bar(decTbl.Decade, decTbl.Avg_Unemployment_Rate);
grid on; xlabel('Decade'); ylabel('Avg Unemployment Rate (%)');
title('Average Unemployment Rate by Decade');

%% 6) Save cleaned table and decadal summary (easy to drop in Streamlit)
if ~exist('output','dir'), mkdir('output'); end
writetable(Tclean, fullfile('output','Annual_Macro_Clean.csv'));
writetable(decTbl, fullfile('output','Annual_Macro_Decadal_Summary.csv'));

disp('Done. Clean CSV and summaries saved in /output');