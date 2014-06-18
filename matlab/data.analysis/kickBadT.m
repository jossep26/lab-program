function goodT = kickBadT(badT)
% Fine tunes signal time found by findSignalTime on noisy data.
% best used in couple with a different signal threshold of findSignalTime
% select bad by interval, too small is considered bad.
THRESHOLD = 1000;
badI = abs(badT - [badT(2:end); badT(end-1)]) < THRESHOLD;
goodT = badT(~badI);

end
