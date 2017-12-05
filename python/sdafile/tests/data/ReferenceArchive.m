% archive name
file='SDAreference.sda';
import SMASH.FileAccess.*

% archive data
a1=zeros(5,1);
a2=1i*ones(4,3);
a3=sparse(eye(5));
a4=[];

b=true;
c='Here is some text';
d=@sin;

% primitive records
archive=SDAfile(file,'overwrite');
insert(archive,'example A1',a1,'5x1 zeros');

writeFile(file,'example A2',a2,'4x3 imaginary numbers');
writeFile(file,'example A3',a3,'5x5 sparse matrix');
writeFile(file,'example A4',a4,'Empty array');

writeFile(file,'example B',b,'Logical scalar');
writeFile(file,'example C',c,'Some text');
writeFile(file,'example D',d,'Handle to the sine function');

% compound records
data={a1 a2};
writeFile(file,'example E',data,'Cell array combining examples A1 and A2');

data=struct('A1',a1,'A2',a2);
writeFile(file,'example F',data,'Structure combining examples A1 and A2');
data=repmat(data,[2 1]);
writeFile(file,'example G',data,'Structure array combining examples A1 and A2 (repeated)');

data=cell(2,1);
data{1}=struct('A1',a1,'A2',a2);
data{2}=struct('A3',a3,'A4',a4);
writeFile(file,'example H',data,'Cell array of structures combining examples A1-A4');

object=ExampleObject();
object.Parameter=a1;
writeFile(file,'example I',object,'Object containing example A1');
object=repmat(object,[2 1]);
object(2).Parameter=a2;
writeFile(file,'example J',object,'Object array containing examples A1 and A2');

% external records
import(archive,'ReferenceArchive.m','MATLAB script for generating a reference archive');

% split records
delete *SampleImage*
z=zeros(10e3);
z(:)=(1:numel(z))/numel(z);
imwrite(z,'SampleImage.png');
splitFile('SampleImage.png','50 kb')