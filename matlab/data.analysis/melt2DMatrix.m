function melted = melt2DMatrix(A)
% melt2DMatrix takes a 2-D numeric matrix A, and turns it into
% a long list of 1-D vector, with row and column indices.
% Output is a 3-column matrix: [rowID colID value]

if ~isnumeric(A)
    return
end

[r c] = ind2sub(size(A), 1:length(A(:)));

melted = [r' c' A(:)];

end