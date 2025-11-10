%% Housing Group 8 — PopulationReport (Super-Robust Student Version)
% Works with odd headers (blank rows / merged cells / "Pop. 2023" text).
% Input : PopulationReport.xlsx (sheet "PopulationReport")
% Output: /output/Population_Clean.csv + PNG figures

clear; clc; close all;

file   = 'PopulationReport.xlsx';
sheet  = 'PopulationReport';
outDir = 'output'; if ~exist(outDir,'dir'), mkdir(outDir); end

%% 1) Read everything as raw; detect header row
Raw = readcell(file, 'Sheet', sheet);
nRows = size(Raw,1); nCols = size(Raw,2);

% helper: convert to string safely
tos = @(x) string(x);

% Find a row that looks like the header:
%   - contains "Name" (any column)
%   - and at least two cells containing "Pop" (e.g., "Pop. 1990")
hdrRow = NaN;
for r = 1:nRows
    row = tos(Raw(r, :));
    row = strtrim(row);
    if any(strcmpi(row, "Name"))
        popHits = sum(contains(lower(row), "pop"));
        if popHits >= 2
            hdrRow = r;
            break;
        end
    end
end
if isnan(hdrRow)
    % fallback: try the row that contains many "Pop" tokens
    bestRow = NaN; bestScore = -inf;
    for r = 1:nRows
        row = tos(Raw(r, :));
        score = sum(contains(lower(row), "pop")) + any(strcmpi(strtrim(row), "Name"));
        if score > bestScore
            bestScore = score; bestRow = r;
        end
    end
    hdrRow = bestRow;
    fprintf('⚠️ Header row not obvious; using row %d based on tokens.\n', hdrRow);
end

% Build header names from hdrRow (strip empties at end)
hdr = tos(Raw(hdrRow, :));
isNonEmpty = ~(hdr == "" | hdr == "NA" | ismissing(hdr));
if ~any(isNonEmpty), error('Header row appears empty.'); end
lastCol = find(isNonEmpty, 1, 'last');
hdr = hdr(1:lastCol);

% Data starts the next row; find last data row (some non-empty in first 2 columns)
dataStart = hdrRow + 1;
isDataRow = false(nRows,1);
for r = dataStart:nRows
    c1 = Raw{r,1}; c2 = []; if lastCol >= 2, c2 = Raw{r,2}; end
    isDataRow(r) = ~( (isempty(c1) || (isstring(c1)&&c1=="") || (ischar(c1)&&strcmp(c1,'')) || (isnumeric(c1)&&isnan(c1))) ...
                   & (isempty(c2) || (isstring(c2)&&c2=="") || (ischar(c2)&&strcmp(c2,'')) || (isnumeric(c2)&&isnan(c2))) );
end
if ~any(isDataRow(dataStart:end))
    error('No data rows found below the detected header row (%d).', hdrRow);
end
dataEnd = find(isDataRow, 1, 'last');

Data = Raw(dataStart:dataEnd, 1:lastCol);
T = cell2table(Data);

% Normalize column names
hdr = regexprep(hdr, '\s+', ' ');            % collapse spaces
hdr = regexprep(hdr, '[^\w\. ]', '');        % drop odd chars
varNames = matlab.lang.makeValidName(cellstr(hdr));
varNames = regexprep(varNames, '[^A-Za-z0-9_]', '_');
varNames = regexprep(varNames, '_+', '_');   % collapse multiple underscores
T.Properties.VariableNames = varNames;

fprintf('Detected header row: %d\n', hdrRow);
disp('Raw column names:'); disp(T.Properties.VariableNames');

%% 2) Map headers to expected names
% Expected targets
expected = {'Name','Pop_1990','Pop_2000','Pop_2010','Pop_2020','Pop_2023','Change_2020_23'};

cur = string(T.Properties.VariableNames);
canon = lower(erase(cur,["_","."," "]));

% helper to find best match for a token like 'Pop_2023'
findMatch = @(token) ...
    find(contains(canon, lower(erase(token,["_","."," "]))), 1, 'first');

idx.Name         = findMatch('Name');
idx.Pop_1990     = findMatch('Pop_1990');
idx.Pop_2000     = findMatch('Pop_2000');
idx.Pop_2010     = findMatch('Pop_2010');
idx.Pop_2020     = findMatch('Pop_2020');
idx.Pop_2023     = findMatch('Pop_2023');
idx.Change_2020_23 = findMatch('Change_2020_23');

% build a standardized table (only columns we can find)
U = table();
if ~isempty(idx.Name),            U.Name            = string(T.(cur(idx.Name))); end
if ~isempty(idx.Pop_1990),        U.Pop_1990        = T.(cur(idx.Pop_1990)); end
if ~isempty(idx.Pop_2000),        U.Pop_2000        = T.(cur(idx.Pop_2000)); end
if ~isempty(idx.Pop_2010),        U.Pop_2010        = T.(cur(idx.Pop_2010)); end
if ~isempty(idx.Pop_2020),        U.Pop_2020        = T.(cur(idx.Pop_2020)); end
if ~isempty(idx.Pop_2023),        U.Pop_2023        = T.(cur(idx.Pop_2023)); end
if ~isempty(idx.Change_2020_23),  U.Change_2020_23  = T.(cur(idx.Change_2020_23)); end

fprintf('✅ Standardized columns present: %s\n', strjoin(U.Properties.VariableNames, ', '));

%% 3) Clean: drop empty names, numeric coercion, remove national row
if ismember('Name', U.Properties.VariableNames)
    U = U(~ismissing(U.Name) & U.Name ~= "", :);
end

numVars = setdiff(U.Properties.VariableNames, {'Name'});
for i = 1:numel(numVars)
    col = U.(numVars{i});
    if iscell(col) || isstring(col) || ischar(col)
        U.(numVars{i}) = str2double(string(col));
    end
end

if ismember('Name', U.Properties.VariableNames)
    U(strcmpi(strtrim(string(U.Name)), "United States"), :) = [];
end

fprintf('✅ Loaded %d data rows after cleaning.\n', height(U));

%% 4) Basic summary + visuals (only if required cols exist)
req = {'Pop_1990','Pop_2023'};
hasReq = all(ismember(req, U.Properties.VariableNames));
if ~hasReq
    warning('Required columns missing for visuals: need Pop_1990 and Pop_2023. Available: %s', strjoin(U.Properties.VariableNames, ', '));
else
    x = U.Pop_2023;
    fprintf('\n=== Summary: Population 2023 ===\n');
    fprintf('Count: %d | Mean: %.0f | Std: %.0f | Min: %.0f | Median: %.0f | Max: %.0f | Sum: %.0f\n', ...
        numel(x), mean(x,'omitnan'), std(x,'omitnan'), min(x), median(x), max(x), sum(x,'omitnan'));

    if ismember('Name', U.Properties.VariableNames)
        [~, idxDesc] = sort(U.Pop_2023, 'descend', 'MissingPlacement','last');
        disp('Top 5 Most Populated (2023):');     disp(string(U.Name(idxDesc(1:min(5,end)))))
        disp('Bottom 5 Least Populated (2023):'); disp(string(U.Name(idxDesc(max(1,end-4):end))))
    end

    % Histogram
    fig1 = figure('Name','Population Distribution (2023)','Position',[80 80 900 480]);
    histogram(U.Pop_2023/1e6, 'BinWidth', 2);
    grid on; box on; xlabel('Population (millions)'); ylabel('Number of States');
    title('Distribution of State Populations (2023)');
    saveas(fig1, fullfile(outDir,'pop_hist_2023.png'));

    % Top 10 (if Name)
    if ismember('Name', U.Properties.VariableNames)
        topN = min(10, height(U));
        top10 = U(idxDesc(1:topN), :);
        fig2 = figure('Name','Top 10 Most Populated States (2023)','Position',[80 80 900 560]);
        barh(categorical(string(top10.Name)), top10.Pop_2023/1e6);
        grid on; box on; xlabel('Population (millions)'); ylabel('State');
        title('Top 10 Most Populated States (2023)');
        saveas(fig2, fullfile(outDir,'top10_pop_2023.png'));
    end

    % Scatter 1990 vs 2023
    fig3 = figure('Name','Population Growth 1990–2023','Position',[80 80 900 620]);
    scatter(U.Pop_1990/1e6, U.Pop_2023/1e6, 38, 'filled'); grid on; box on;
    xlabel('Population 1990 (millions)'); ylabel('Population 2023 (millions)');
    title('State Population Growth (1990 → 2023)');
    lims = [0, max([U.Pop_1990; U.Pop_2023], [], 'omitnan')/1e6*1.05];
    hold on; plot(lims, lims, '--', 'LineWidth', 1);
    xlim(lims); ylim(lims); legend({'State','y = x'}, 'Location','northwest');
    saveas(fig3, fullfile(outDir,'scatter_1990_vs_2023.png'));
end

%% 5) Save cleaned output
writetable(U, fullfile(outDir,'Population_Clean.csv'));
disp('✅ Clean table saved in /output');