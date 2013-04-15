function m=bot(im,roi)

[a b imNumber]=size(im);
m=zeros(length(roi),imNumber);

for i=1:length(roi)
    mIm=reshape(im(roi(i).ygrid,roi(i).xgrid,:),length(roi(i).ygrid),length(roi(i).xgrid)*imNumber);
    mBW=repmat(roi(i).BW(roi(i).ygrid,roi(i).xgrid),1,imNumber);
    mIm=mIm.*int16(mBW);
    xIm=reshape(mIm,length(roi(i).ygrid).*length(roi(i).xgrid),imNumber);
    m(i,:)=sum(xIm,1)./sum(roi(i).BW(:));
end
 m=m';
return
    