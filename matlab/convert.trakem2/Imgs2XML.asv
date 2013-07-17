clear;
clc;
close all;

be=40;
en=89;
prefix='i:\data\zby\EM.reconstruction\20130507-a\';
src_prefix='i:\data\zby\EM.reconstruction\20130507-a\';
filename=[prefix,'I00040_overlay.tif'];
img=imread(filename);
[idy,idx]=find(img(:,:,2)==255);

fin=fopen('i:\data\zby\EM.reconstruction\20130507-a\base_stack.xml');
fout=fopen('i:\data\zby\EM.reconstruction\20130507-a\dst_stack.xml','w');
id=20;
k=1;
while k<=324
    if k==316
        str = fgetl(fin);
        str = fgetl(fin);
        fprintf(fout,'			width="%d.0"\n',size(img,2));
        fprintf(fout,'			height="%d.0"\n',size(img,1));
        k=k+2;
        continue;
    end
    if k==285
        str = fgetl(fin);
        str = fgetl(fin);
        fprintf(fout,'		layer_width="%d.0"\n',size(img,2));
        fprintf(fout,'		layer_height="%d.0"\n',size(img,1));
        k=k+2;
        continue;
    end
    str=fgetl(fin);
    fprintf(fout,'%s\n',str);
    k=k+1;
end

curid=id;
for i=be:en
    filename=[prefix,'I000',num2str(i),'_overlay.tif'];
    img=imread(filename);
    [idy,idx]=find(img(:,:,2)==255);
    fprintf(fout,'			<t2_area layer_id="%d">\n',id);
    fprintf(fout,'				<t2_path d="M 0 0 L 0 1 L 1 1 L 1 0 z" />\n');
    a=size(img,2)-1;
    b=size(img,1)-1;
    fprintf(fout,'				<t2_path d="M %d %d L %d %d L %d %d L %d %d z" />\n',a,b,a,b+1,a+1,b+1,a+1,b);
    for j=1:size(idx,1)
        a=idx(j,1)-1;
        b=idy(j,1)-1;
        fprintf(fout,'				<t2_path d="M %d %d L %d %d L %d %d L %d %d z" />\n',a,b,a,b+1,a+1,b+1,a+1,b);
    end
    fprintf(fout,'			</t2_area>\n');
    id=id+2;
end
id=curid;
fprintf(fout,'		</t2_area_list>\n');
for i=be:en
    filename=['I000',num2str(i),'_image.tif'];
    fprintf(fout,'		<t2_layer oid="%d"\n',id);
    fprintf(fout,'			 thickness="1.0"\n');
    fprintf(fout,'			 z="%d.0"\n',i-be);
    fprintf(fout,'			 title=""\n');
    fprintf(fout,'		>\n');
    fprintf(fout,'			<t2_patch\n');
    fprintf(fout,'				oid="%d"\n',id+1);
    fprintf(fout,'				width="%d.0"\n',size(img,2));
    fprintf(fout,'			    height="%d.0"\n',size(img,1));
    fprintf(fout,'				transform="matrix(1.0,0.0,0.0,1.0,0.0,0.0)"\n');
    fprintf(fout,'				title="%s"\n',filename);
    if i==be
        fprintf(fout,'				links="%d"\n',id+3);
    end
    if i>be&&i<en
        fprintf(fout,'				links="%d,%d"\n',id-1,id+3);
    end
    if i==en
        fprintf(fout,'				links="%d"\n',id-1);
    end
    fprintf(fout,'				type="0"\n');
    filename=[src_prefix,'I000',num2str(i),'_image.tif'];
    fprintf(fout,'				file_path="%s"\n',filename);
    fprintf(fout,'				style="fill-opacity:1.0;stroke:#00ff00;"\n');
    fprintf(fout,'				o_width="%d"\n',size(img,2));
    fprintf(fout,'				o_height="%d"\n',size(img,1));
    fprintf(fout,'				min="0.0"\n');
    fprintf(fout,'				max="255.0"\n');
    fprintf(fout,'				mres="32"\n');
    fprintf(fout,'			>\n');
    fprintf(fout,'			</t2_patch>\n');
    fprintf(fout,'		</t2_layer>\n');
    id=id+2;
end

fprintf(fout,'	</t2_layer_set>\n');
fprintf(fout,'</trakem2>\n');

fclose(fin);
fclose(fout);