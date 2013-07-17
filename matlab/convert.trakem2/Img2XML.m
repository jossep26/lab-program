clear;
clc;
close all;

filename='mitochondrion_dup.bmp';
color_img=imread(filename);
[idx,idy]=find(color_img(:,:,2)==255);

filename='mitochondrion.bmp';
img=imread(filename);

fin=fopen('base.xml');
fout=fopen('dst.xml','w');
str=fgetl(fin);
k=1;
while ischar(str)
    fprintf(fout,'%s\n',str);
    if k==315
        str = fgetl(fin);
        str = fgetl(fin);
        fprintf(fout,'			width="%d.0"\n',size(img,2));
        fprintf(fout,'			height="%d.0"\n',size(img,1));
        k=k+2;
    end
    if k==324
        fprintf(fout,'			<t2_area layer_id="5">\n');
        fprintf(fout,'				<t2_path d="M 0 0 L 0 1 L 1 1 L 1 0 z" />\n');
        a=size(img,2);
        b=size(img,1);
        fprintf(fout,'				<t2_path d="M %d %d L %d %d L %d %d L %d %d z" />\n',a,b,a,b+1,a+1,b+1,a+1,b);
        for i=1:size(idx,1)
            a=idx(i,1);
            b=idy(i,1);
            fprintf(fout,'				<t2_path d="M %d %d L %d %d L %d %d L %d %d z" />\n',a,b,a,b+1,a+1,b+1,a+1,b);
        end
        fprintf(fout,'			</t2_area>\n');
    end
    str = fgetl(fin);
    k=k+1;
end

fclose(fin);
fclose(fout);