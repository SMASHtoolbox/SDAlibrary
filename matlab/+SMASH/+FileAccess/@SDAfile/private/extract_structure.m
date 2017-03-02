function data=extract_structure(archive,setname)

file=archive.ArchiveFile;

% extract field names
name=cell(0);
temp=readAttribute(file,setname,'FieldNames');
while ~isempty(temp)
    [new,~,~,next]=sscanf(temp,'%s',1);
    if ~isempty(new)
        name{end+1}=new; %#ok<AGROW>
    end
    temp=temp(next:end);
end

data=struct();
for k=1:numel(name)
    local=[setname '/' name{k}];
    switch readAttribute(file,local,'RecordType')
        case 'numeric'
            data.(name{k})=extract_numeric(archive,local);
        case 'logical'
            data.(name{k})=extract_logical(archive,local);
        case 'character'
            data.(name{k})=extract_character(archive,local);
        case 'function'
            data.(name{k})=extract_function(archive,local);
        case 'structure'
            data.(name{k})=extract_structure(archive,local);
        case 'cell'
            data.(name{k})=extract_cell(archive,local);
        case 'object'
            data.(name{k})=extract_object(archive,local);                       
        otherwise
            error('ERROR: invalid record type');
    end
end

end