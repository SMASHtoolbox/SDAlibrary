function insert_object(archive,datasetname,data,deflate)

% convert objects to structures
ObjectClass=class(data);
if isscalar(data)
    data=object2structure(data);
    insert_structure(archive,datasetname,data,deflate);
    h5writeatt(archive.ArchiveFile,['/' datasetname],'RecordType','object');
    h5writeatt(archive.ArchiveFile,['/' datasetname],'Class',ObjectClass);
else
    %message={};
    %message{end+1}='Object arrays are not supported in SDA files';
    %message{end+1}='Converting object array to a cell array of objects';
    %warning('SMASH:SDA','%s\n',message{:});
    temp=cell(size(data));
    for n=1:numel(data)
        temp{n}=data(n);
    end
    insert_cell(archive,datasetname,temp,deflate);
    h5writeatt(archive.ArchiveFile,['/' datasetname],'RecordType','objects');
    h5writeatt(archive.ArchiveFile,['/' datasetname],'Class',ObjectClass);
end

end