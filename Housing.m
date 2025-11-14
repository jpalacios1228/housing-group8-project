%% Housing Group 8 - Housing Dataset
% Author: Arian Milicija
% Goal: Perform simple cleaning, summaries, and visuals on housing data
% Dataset: Housing.xlsx (sheet 'in')

clear; clc; close all;

%% 1) Load dataset
file = 'Housing.xlsx';
sheet = 'in';
T = readtable(file, 'Sheet', sheet);

%% 2) Handle missing or invalid values
% Check missing counts
disp('Missing values per column:');
disp(sum(ismissing(T)));

% Convert numeric columns to double (if needed)
numVars = {'price','area','bedrooms','bathrooms','stories','parking'};
for i = 1:numel(numVars)
    if iscell(T.(numVars{i})) || isstring(T.(numVars{i})) || ischar(T.(numVars{i}))
        T.(numVars{i}) = str2double(string(T.(numVars{i})));
    end
end

% Drop any rows missing a price or area (key features)
Tclean = T(~(ismissing(T.price) | ismissing(T.area)), :);

fprintf('✅ Cleaned dataset: %d rows remaining.\n', height(Tclean));

%% 3) Summary statistics for Price (like "Total Spent" example)
x = Tclean.price;
fprintf('\n=== Summary Statistics for Price ===\n');
fprintf('Count: %d\n', numel(x));
fprintf('Mean: %.2f\n', mean(x,'omitnan'));
fprintf('Std: %.2f\n', std(x,'omitnan'));
fprintf('Min: %.2f\n', min(x));
fprintf('Median: %.2f\n', median(x));
fprintf('Max: %.2f\n', max(x));
fprintf('Sum: %.2f\n', sum(x));

%% 4) Most common features (analogue to "mostly sold item / payment method")
% Mode for categorical variables
fprintf('\n=== Most Common Features ===\n');
fprintf('Most common furnishing status: %s\n', string(mode(categorical(Tclean.furnishingstatus))));
fprintf('Most common air conditioning: %s\n', string(mode(categorical(Tclean.airconditioning))));
fprintf('Most common basement presence: %s\n', string(mode(categorical(Tclean.basement))));

%% 5) Visualizations

% Histogram of Price
figure('Name','Price Distribution');
histogram(Tclean.price, 20);
xlabel('Price'); ylabel('Count'); title('Distribution of House Prices');
grid on;

% Scatter: Area vs Price
figure('Name','Area vs Price');
scatter(Tclean.area, Tclean.price, 30, 'filled');
xlabel('Area'); ylabel('Price');
title('House Price vs Area');
grid on;

% Boxplot: Price by Furnishing Status
figure('Name','Price by Furnishing');
boxchart(categorical(Tclean.furnishingstatus), Tclean.price);
xlabel('Furnishing Status'); ylabel('Price');
title('Price by Furnishing Status');
grid on;

% Bar Chart: Average Price by Number of Bedrooms
bedStats = groupsummary(Tclean, "bedrooms", "mean", "price");
figure('Name','Average Price by Bedrooms');
bar(bedStats.bedrooms, bedStats.mean_price);
xlabel('Bedrooms'); ylabel('Average Price');
title('Average Price by Number of Bedrooms');
grid on;

% Pie Chart: Furnishing Status
counts = groupcounts(categorical(Tclean.furnishingstatus));
labels = categories(categorical(Tclean.furnishingstatus));
figure('Name','Pie - Furnishing Status');
pie(counts, labels);
title('Furnishing Status Distribution');

% Bar Chart: Parking vs Average Price
parkStats = groupsummary(Tclean, "parking", "mean", "price");
figure('Name','Average Price by Parking Spots');
bar(parkStats.parking, parkStats.mean_price);
xlabel('Parking Spots'); ylabel('Average Price');
title('Average Price by Number of Parking Spots');
grid on;

%% 6) Save outputs
if ~exist('output','dir'), mkdir('output'); end
writetable(Tclean, fullfile('output','Housing_Clean.csv'));
disp('Clean dataset saved to /output/Housing_Clean.csv');