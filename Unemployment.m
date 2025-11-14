%% Housing Group 8 — Unemployment Report (Auto-Detect % Column, v3)
clear; clc; close all;

inFile  = 'UnemploymentReport.xlsx';
inSheet = 'UnemploymentReport';
outDir  = 'output'; if ~exist(outDir,'dir'), mkdir(outDir); end

%% Load sheet without trusting headers
Raw = readcell(inFile, 'Sheet', inSheet);
[nRows, nCols] = size(Raw);

isemptycell = @(v) (isempty(v) || (isstring(v)&&v=="") || (ischar(v)&&strcmp(v,'')) || (isnumeric(v)&&isnan(v)));
tos = @(x) string(x);

% pick the row that looks the most like a header
bestRow = NaN; bestScore = -Inf;
for r = 1:nRows
    s = lower(strtrim(tos(Raw(r,:))));
    nonEmpty = sum(~arrayfun(isemptycell, Raw(r,:)));
    keyHits  = sum(contains(s, ["unemploy","rate","percent","pct","lower","upper","bound","name","state","region","fips"]));
    score = nonEmpty + 2*keyHits;
    if score > bestScore, bestScore = score; bestRow = r; end
end
hdrRow = bestRow;
hdr    = tos(Raw(hdrRow,:));
lastCol = find(~(hdr=="" | ismissing(hdr)), 1, 'last'); if isempty(lastCol), error('Header row empty.'); end
hdr    = hdr(1:lastCol);

dataStart = hdrRow+1;
isDataRow = false(nRows,1);
for r = dataStart:nRows
    c1 = Raw{r,1}; c2 = []; if lastCol>=2, c2 = Raw{r,2}; end
    isDataRow(r) = ~(isemptycell(c1) & isemptycell(c2));
end
if ~any(isDataRow(dataStart:end)), error('No data rows under header.'); end
dataEnd = find(isDataRow,1,'last');

Data = Raw(dataStart:dataEnd, 1:lastCol);
T = cell2table(Data);

names = matlab.lang.makeValidName(cellstr(hdr));
names = regexprep(names,'[^A-Za-z0-9_]','_'); names = regexprep(names,'_+','_');
names = matlab.lang.makeUniqueStrings(names);
T.Properties.VariableNames = names;

%% Choose label column (state/region)
v = string(T.Properties.VariableNames); lv = lower(v);
nameIdx = find(contains(lv, ["name","state","region","area","geo"]), 1, 'first');
if isempty(nameIdx), nameIdx = 1; v(nameIdx)="Name"; T.Properties.VariableNames=cellstr(v); lv=lower(v); end

U = table; U.Name = string(T.(T.Properties.VariableNames{nameIdx}));
U = U(~ismissing(U.Name) & U.Name~="", :);  % drop blank names

%% Score all candidate numeric columns to find the unemployment percentage
badHdr = contains(lv, ["fips","code","id","number","cnt","count","total"]);
candIdx = setdiff( find(~badHdr & ( (1:numel(lv))~=nameIdx )), nameIdx );

best = struct('idx',[], 'scale',1, 'score',-Inf, 'median',NaN, 'p90',NaN, 'maxv',NaN, 'hdr','');

debugRows = [];

for idx = candIdx(:)'
    hdrName = T.Properties.VariableNames{idx};

    % coerce to numeric, stripping % and commas
    rawVals = string(T.(hdrName));
    rawVals = erase(rawVals, "%"); rawVals = erase(rawVals, ",");
    vals = str2double(rawVals);
    vals = vals(1:min(height(U), numel(vals)));

    finiteMask = isfinite(vals);
    fracFinite = mean(finiteMask);
    if fracFinite < 0.75, continue; end   % need mostly numeric

    medv = median(vals,'omitnan');
    p90  = prctile(vals,90);   % robust upper spread
    mx   = max(vals,[],'omitnan');

    % Heuristics:
    %   prefer 0-20 range or (0-1 range -> fraction)
    score = 0;
    hdrLower = lower(hdrName);
    if contains(hdrLower,"unemploy") || contains(hdrLower,"rate") || contains(hdrLower,"percent") || contains(hdrLower,"pct")
        score = score + 3;
    end
    if (p90 <= 20 && mx <= 100 && medv >= 2 && medv <= 12)
        score = score + 5;  % looks like percent already
        proposedScale = 1;
    elseif (p90 <= 1.0 && mx <= 1.2 && medv >= 0.02 && medv <= 0.12)
        score = score + 4;  % looks like fraction
        proposedScale = 100;
    else
        % penalize integer-heavy large columns (likely codes or counts)
        intLike = mean(abs(vals - round(vals)) < 1e-9, 'omitnan');
        if intLike > 0.9 && mx>50, score = score - 4; end
        % mild acceptance if mostly <=100
        if mx<=100 && p90<=30, score = score + 1; end
        proposedScale = 1;
    end

    % store for debug table
    debugRows = [debugRows; {hdrName, fracFinite, medv, p90, mx, score, proposedScale}];

    if score > best.score
        best.idx   = idx;
        best.scale = proposedScale;
        best.score = score;
        best.median= medv; best.p90=p90; best.maxv=mx; best.hdr=hdrName;
    end
end

% Show candidates for transparency
fprintf('\nCandidate columns (most numeric → least filtered):\n');
fprintf('%-30s  finite%%  median   p90     max     score  scale\n');
if ~isempty(debugRows)
    for i=1:size(debugRows,1)
        fprintf('%-30s  %6.2f  %7.2f  %6.2f  %7.2f   %5.1f   x%3d\n', ...
            debugRows{i,1}, debugRows{i,2}, debugRows{i,3}, debugRows{i,4}, debugRows{i,5}, debugRows{i,6}, debugRows{i,7});
    end
end

assert(~isempty(best.idx) && isfinite(best.score), 'Could not detect a credible unemployment rate column.');

% Build numeric percent column
vals = string(T.(T.Properties.VariableNames{best.idx}));
vals = erase(vals, "%"); vals = erase(vals, ",");
vals = str2double(vals); vals = vals(1:height(U));
U.Unemployment_Pct = vals * best.scale;

%% Final cleaning
U(strcmpi(strtrim(U.Name),'United States'), :) = [];

% Drop rows whose "Name" is all digits (FIPS-like) or starts with digits
isAllDigits = ~cellfun('isempty', regexp(cellstr(U.Name), '^\d+$', 'once'));
U = U(~isAllDigits, :);

% Keep only sensible 0..100 %
U = U(U.Unemployment_Pct>=0 & U.Unemployment_Pct<=100, :);

fprintf('\n✅ Using column "%s" (scale x%d). Rows kept: %d\n', best.hdr, best.scale, height(U));

%% Simple stats + plots
x = U.Unemployment_Pct;
fprintf('\n=== Summary: Unemployment Rate (%%) ===\n');
fprintf('Count: %d | Mean: %.2f | Std: %.2f | Min: %.2f | Median: %.2f | Max: %.2f\n', ...
    numel(x), mean(x,'omitnan'), std(x,'omitnan'), min(x), median(x), max(x));

[~, idxDesc] = sort(x,'descend','MissingPlacement','last');
topN = min(10, height(U)); top10 = U(idxDesc(1:topN), {'Name','Unemployment_Pct'});

fig1 = figure('Name','Histogram - Unemployment Rate','Position',[80 80 900 480]);
histogram(x, 15); grid on; box on;
xlabel('Unemployment rate (%)'); ylabel('Number of states');
title('Distribution of Unemployment Rates');
saveas(fig1, fullfile(outDir,'unemployment_hist.png'));

fig2 = figure('Name','Top 10 Highest Unemployment','Position',[80 80 900 560]);
cats = categorical(string(top10.Name)); cats = reordercats(cats, string(top10.Name));
barh(cats, top10.Unemployment_Pct); grid on; box on;
xlabel('Unemployment rate (%)'); ylabel('State');
title('Top 10 Highest Unemployment');
xlim([0, max(top10.Unemployment_Pct)*1.15]);
saveas(fig2, fullfile(outDir,'unemployment_top10.png'));

writetable(U, fullfile(outDir,'Unemployment_Clean.csv'));
disp('✅ Clean table and figures saved in /output');