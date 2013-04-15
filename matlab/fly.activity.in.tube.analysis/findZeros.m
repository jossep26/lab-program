function result = findZeros(vec)
% Find consecutive zeros in a vector.

% Requires function 'rude': http://www.mathworks.com/matlabcentral/fileexchange/6436

% Find repetitive patterns in vec, using 'rude'
[len, val] = rude(vec);

% Apply criteria: number of repeats greater than 5, and value equals 0
idx = intersect(find(len>=5), find(val==0));

% Get begin and end index from 'len'
indexEnd = cumsum(len);
indexBegin = [1 indexEnd(1:(end-1))+1];

% Get the results indexes of the original vector
idxBegin = indexBegin(idx);
idxEnd = indexEnd(idx);

result = idxEnd - idxBegin + 1;

end