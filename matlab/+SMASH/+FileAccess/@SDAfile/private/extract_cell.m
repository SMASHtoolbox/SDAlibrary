function data=extract_cell(archive,setname)

file=archive.ArchiveFile;
empty=readAttribute(file,setname,'Empty');
if strcmp(empty,'yes')
    data={};
    return
end

Lsize=readAttribute(file,setname,'RecordSize');
N=numel(Lsize);
Lsize=reshape(Lsize,[1 N]);
data=cell(Lsize);
for k=1:numel(data)
    local=[setname '/' sprintf('element %d',k)];
    switch readAttribute(file,local,'RecordType')
        case 'numeric'
            data{k}=extract_numeric(archive,local);
        case 'logical'
            data{k}=extract_logical(archive,local);
        case 'character'
            data{k}=extract_character(archive,local);
        case 'function'
            data{k}=extract_function(archive,local);
        case 'structure'
            data{k}=extract_structure(archive,local);
        case 'cell'
            data{k}=extract_cell(archive,local);
        case 'object'
            data{k}=extract_object(archive,local);           
        otherwise
    end
end

end