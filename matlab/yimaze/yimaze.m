% load avi
%clear
mv=mmreader('D:\Yi-maze\matlab\cs_02_MCH_L.avi');
im=read(mv);
imm=double(squeeze(im(:,:,1,:)));
mvfreq=mv.FrameRate;
mvlength=120*mvfreq;

imm_mean=(mean(imm,3));
%figure;imagesc(imm_mean);
for i=1:mvlength
    diff(:,:,i)=imm(:,:,i)-imm_mean; %每一帧与平均的差异；
    %flies=sum(diff(:,:,i)>mean(diff,2))
 end;
 %sum_fly=size(find(diff(:,:,:)>mean(diff,2)));
figure;imagesc(diff(:,:,200));


