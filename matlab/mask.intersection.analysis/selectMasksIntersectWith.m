function selectedMasks = selectMasksIntersectWith(masks, withMask, NCOMMONPIX)

% Select the masks that intersect with another mask.
% NCOMMONPIX sets the least number of overlapping pixels.
% The output cell header: 
%       {'selected_mask', 'overlap_mask', 'no_in_original_masks'}

if ~iscell(masks)
    masks = {masks};
end

selectedMasks = cell(1,3);
iSelected = 0;
for iMask = 1:length(masks)
    intersectedMask = masks{iMask} & withMask;
    if sum(intersectedMask(:)) >= NCOMMONPIX
       selectedMasks{iSelected+1,1} = masks{iMask};
       selectedMasks{iSelected+1,2} = intersectedMask;
       selectedMasks{iSelected+1,3} = iMask;
       iSelected = iSelected + 1;
    end
end

end