function data=extract_logical(archive,setname)

file=archive.ArchiveFile;
empty=h5readatt(file,setname,'Empty');
if strcmp(empty,'yes')
    empty=true;
else
    empty=false;
end

if empty
    data=[];
else
    data=h5read(file,setname);
    data=logical(data);
end

end