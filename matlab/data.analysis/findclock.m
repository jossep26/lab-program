function [result offset]=findclock(clock,event)
% result=findclock(clock,event)
% find the time of events relative to the clock
% Feb 20 2009 Li Hao

cycle=length(event);
result=zeros(1,cycle);
offset=zeros(1,cycle);
for i=1:cycle
    [offset(i) result(i)]=min(abs(clock-event(i)));
end
return