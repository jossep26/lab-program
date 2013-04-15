function [t_up t_down]=timing_old(data)

[up down]=th(data(:,1),2.5);
[up2 down2]=th(data(:,2),.6);
[t_up offset]=findclock(up,up2);
[t_down offset2]=findclock(up,down2);
% delta=ceil(mean(t_down-t_up));
figure;plot(offset/1e4);hold on;plot(offset2/1e4,'r');

return


function [up down]=th(data,threshold)

data2=[data(2:end); data(end)];

up=find(data<threshold & data2>threshold);
down=find(data>threshold & data2<threshold);

if numel(up) ~= numel(down)
    warning('Number of rising edges unequal to the number of falling edges');
else
%     figure;plot(down-up);
end
% delta=down-up;

return


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