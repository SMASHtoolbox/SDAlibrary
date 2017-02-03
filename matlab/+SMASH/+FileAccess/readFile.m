% READFILE Read from a text or binary file
%
% This function reads various text and binary file formats. To read from a
% specific file, use the command:
%    >> data=readFile(filename,[format],[record]);
% The second and third inputs are optional in many situations.
%    -"format" should be specified if the file's extension is associated
%    with more than one format (such as *.img).  If omitted, the user will
%    be prompted to select a format that is consistent with the extension.
%    An empy string ('') can be passed as a placeholder when there is no
%    format ambiguity.
%    -"record" is used only in 'column' and multi-record ('sda', 'pff',
%    etc.) formats.
% If no inputs are used:
%    >> data=readFile;
% or an empty file name is used, the user is prompted to select a file.
%  
% The output "data" is a format-dependent structure array.  When a specific
% file is selected, this array has a single entry.  File names containing
% wild cards (e.g., '*.txt') may return a multi-dimensional structure
% array.  Each element of this array corresponds to a single file import.
%
% See also SMASH.FileAccess
%

% 
% created November 2, 2014 by Daniel Dolan (Sandia National Laboratory)
%
function [data,format]=readFile(filename,format,record)

% handle file name
if nargin<1
    filename='';
end

if nargin<2
    format='';
end

if isempty(filename) || isempty(format)
   [format,filename]=determineFormat(filename,format);
end

if nargin<3
    record=[];
end

% handle wildcards
if any(filename=='*') % handle wild cards
    [pathname,filename,ext]=fileparts(filename);
    if isempty(pathname)
        pathname=pwd;
    end
    name=dir(fullfile(pathname,[filename ext]));
    Nfile=numel(name);
    for k=1:Nfile
        temp=fullfile(pathname,name(k).name);
        [temp,format]=SMASH.FileAccess.readFile(temp,format,record);
        if k==1
            data=repmat(temp,1,Nfile);
        else
            data(k)=temp;
        end
    end
    return
end

% create object based on format
switch format
    case 'column'
        object=SMASH.FileAccess.ColumnFile(filename);
        data=read(object);
        if isempty(record)
            return
        end
        try
            data.Data=data.Data(:,record); 
        catch
            error('ERROR: invalid column request');
        end
    case 'block'
        object=SMASH.FileAccess.BlockFile(filename);
        data=read(object);                
    case {'oceanoptics','optronicslab','optronicslabdump'}
        object=SMASH.FileAccess.CustomFile(filename,format);
        data=read(object);
    case {'acqiris','agilent','keysight','lecroy','tektronix','yokogawa'}
        object=SMASH.FileAccess.DigitizerFile(filename,format);
        data=read(object,record);
    case {'zdas','saturn'}
        object=SMASH.FileAccess.DigitizerFile(filename,format);
        data=read(object,record);
    case 'dig'
        object=SMASH.FileAccess.DIGfile(filename);
        data=read(object);
    case {'film','plate','winspec','sbfp','optronis','hamamatsu','graphics','sydor'}
        object=SMASH.FileAccess.ImageFile(filename,format);
        data=read(object,record);
    case 'pff'
        object=SMASH.FileAccess.PFFfile(filename);
        data=read(object,record);
    case 'sda'
        archive=SMASH.FileAccess.SDAfile(filename);
        data=extract(archive,record);        
    otherwise
        error('ERROR: invalid file format');
end

end