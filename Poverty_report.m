%% Housing Group 8 — Poverty Report (Dup-Header Safe)
% Input : PovertyReport.xlsx (sheet "PovertyReport")
% Output: /output/Poverty_Clean.csv + PNG figures

clear; clc; close all;

inFile  = 'PovertyReport.xlsx';
inSheet = 'PovertyReport';
outDir  = 'output';
if ~exist(outDir,'dir'), mkdir(outDir); end

%% 1) Read raw (no headers) + detect header row where first nonempty cell == "Name"
Raw = readcell(inFile, 'Sheet', inSheet);
nRows = size(Raw,1); nCols = size(Raw,2);

% helper to test emptiness
isemptycell = @(v) (isempty(v) || (isstring(v)&&v=="") || (ischar(v)&&strcmp(v,'')) || (isnumeric(v)&&isnan(v)));

hdrRow = NaN;
for r = 1:nRows
    % first non-empty cell in this row
    cidx = find(~cellfun(isemptycell, Raw(r,:)), 1, 'first');
    if ~isempty(cidx)
        val = Raw{r,cidx};
        if ischar(val) || isstring(val)
            if strcmpi(strtrim(string(val)), 'Name')
                hdrRow = r; break;
            end
        end
    end
end
if isnan(hdrRow), error('Header row not found (row containing "Name").'); end

% Build header names from hdrRow, trim trailing empties
hdr = string(Raw(hdrRow, :));
lastCol = find(~(hdr=="" | ismissing(hdr)), 1, 'last');
if isempty(lastCol), error('Header row appears empty.'); end
hdr = hdr(1:lastCol);

% Data block: from next row until last row that has anything in first two cols
dataStart = hdrRow + 1;
isDataRow = false(nRows,1);
for r = dataStart:nRows
    c1 = Raw{r,1}; c2 = []; if lastCol >= 2, c2 = Raw{r,2}; end
    isDataRow(r) = ~(isemptycell(c1) & isemptycell(c2));
end
if ~any(isDataRow(dataStart:end)), error('No data rows found beneath the header.'); end
dataEnd = find(isDataRow, 1, 'last');

Data = Raw(dataStart:dataEnd, 1:lastCol);
T = cell2table(Data);

% ---- Make valid, normalized, and UNIQUE variable names (fixes your error) ----
rawNames = matlab.lang.makeValidName(cellstr(hdr));           % legal identifiers
rawNames = regexprep(rawNames, '[^A-Za-z0-9_]', '_');         % strip odd chars
rawNames = regexprep(rawNames, '_+', '_');                    % collapse __
rawNames = matlab.lang.makeUniqueStrings(rawNames);           % ensure uniqueness
T.Properties.VariableNames = rawNames;

%% 2) Identify columns (robust to duplicates)
names  = string(T.Properties.VariableNames);
lnames = lower(names);

% Name column
nameIdx = find(contains(lnames, "name"), 1, 'first');
assert(~isempty(nameIdx), 'Could not find "Name" column.');

% All percent/lower/upper columns (there are two blocks: All People, Children)
percentIdx = find(contains(lnames, "percent"));
lbIdx      = find(contains(lnames, "lower"));
ubIdx      = find(contains(lnames, "upper"));

% We need at least two percent columns (one for All, one for Children)
assert(numel(percentIdx) >= 2, 'Could not find two "Percent" columns.');

% Sort by column position (left -> right)
percentIdx = sort(percentIdx);
lbIdx = sort(lbIdx);
ubIdx = sort(ubIdx);

% Assign first Percent = All, second Percent = Children
idxAll_percent   = percentIdx(1);
idxChild_percent = percentIdx(2);

% For each Percent, take the first LB/UB that appear to its right
idxAll_lb   = lbIdx(find(lbIdx > idxAll_percent, 1, 'first'));
idxAll_ub   = ubIdx(find(ubIdx > idxAll_percent, 1, 'first'));
idxCh_lb    = lbIdx(find(lbIdx > idxChild_percent, 1, 'first'));
idxCh_ub    = ubIdx(find(ubIdx > idxChild_percent, 1, 'first'));

assert(~isempty(idxAll_lb) && ~isempty(idxAll_ub) && ~isempty(idxCh_lb) && ~isempty(idxCh_ub), ...
    'Could not align Lower/Upper bounds with Percent columns.');

%% 3) Build clean table U
U = table;
U.Name                 = string(T.(names(nameIdx)));
U.All_Poverty_Pct      = T.(names(idxAll_percent));
U.All_Lower_Bound      = T.(names(idxAll_lb));
U.All_Upper_Bound      = T.(names(idxAll_ub));
U.Children_Poverty_Pct = T.(names(idxChild_percent));
U.Children_Lower_Bound = T.(names(idxCh_lb));
U.Children_Upper_Bound = T.(names(idxCh_ub));

% Drop empty-name rows
U = U(~ismissing(U.Name) & U.Name ~= "", :);

% Coerce numerics (in case anything came in as text)
for v = 2:width(U)
    col = U.(v);
    if iscell(col) || isstring(col) || ischar(col)
        U.(v) = str2double(string(col));
    end
end

% Remove national aggregate if present
U(strcmpi(strtrim(U.Name), "United States"), :) = [];

fprintf('✅ Cleaned %d rows. Columns: %s\n', height(U), strjoin(U.Properties.VariableNames, ', '));

%% 4) Simple stats
x  = U.All_Poverty_Pct;
xc = U.Children_Poverty_Pct;

fprintf('\n=== Summary: All People in Poverty (%%, 2023) ===\n');
fprintf('Count: %d | Mean: %.2f | Std: %.2f | Min: %.2f | Median: %.2f | Max: %.2f\n', ...
    numel(x), mean(x,'omitnan'), std(x,'omitnan'), min(x), median(x), max(x));

fprintf('\n=== Summary: Children (0–17) in Poverty (%%, 2023) ===\n');
fprintf('Count: %d | Mean: %.2f | Std: %.2f | Min: %.2f | Median: %.2f | Max: %.2f\n', ...
    numel(xc), mean(xc,'omitnan'), std(xc,'omitnan'), min(xc), median(xc), max(xc));

[~, idxDesc] = sort(U.All_Poverty_Pct, 'descend', 'MissingPlacement','last');
topN = min(10, height(U));
disp('Top 10 Highest Poverty (All people, %):');
disp(U(idxDesc(1:topN), {'Name','All_Poverty_Pct'}));

%% 5) Visuals (simple & clear)
% Histogram: All people
fig1 = figure('Name','Histogram - All People in Poverty (2023)','Position',[80 80 900 480]);
histogram(U.All_Poverty_Pct, 15); grid on; box on;
xlabel('Poverty rate (%), All people'); ylabel('Number of states');
title('Distribution of Poverty Rates (All People, 2023)');
saveas(fig1, fullfile(outDir,'poverty_all_hist.png'));

% Histogram: Children
fig2 = figure('Name','Histogram - Children Poverty (2023)','Position',[80 80 900 480]);
histogram(U.Children_Poverty_Pct, 15); grid on; box on;
xlabel('Poverty rate (%), Children 0–17'); ylabel('Number of states');
title('Distribution of Poverty Rates (Children, 2023)');
saveas(fig2, fullfile(outDir,'poverty_children_hist.png'));

% Barh: Top 10 (All people)
fig3 = figure('Name','Top 10 Highest Poverty (All People)','Position',[80 80 900 560]);
cats = categorical(string(U.Name(idxDesc(1:topN))));
cats = reordercats(cats, string(U.Name(idxDesc(1:topN))));
barh(cats, U.All_Poverty_Pct(idxDesc(1:topN))); grid on; box on;
xlabel('Poverty rate (%)'); ylabel('State');
title('Top 10 Highest Poverty (All People, 2023)');
saveas(fig3, fullfile(outDir,'poverty_all_top10.png'));

% Scatter: Children vs All
fig4 = figure('Name','Children vs All Poverty Rates (2023)','Position',[80 80 900 620]);
scatter(U.All_Poverty_Pct, U.Children_Poverty_Pct, 36, 'filled'); grid on; box on;
xlabel('All people poverty rate (%)'); ylabel('Children 0–17 poverty rate (%)');
title('Children vs All Poverty Rates (2023)');
lims = [0, max([U.All_Poverty_Pct; U.Children_Poverty_Pct], [], 'omitnan')*1.05];
hold on; plot(lims, lims, '--'); xlim(lims); ylim(lims);
saveas(fig4, fullfile(outDir,'poverty_children_vs_all_scatter.png'));

%% 6) Save cleaned output
writetable(U, fullfile(outDir,'Poverty_Clean.csv'));
disp('✅ Clean table and figures saved in /output');