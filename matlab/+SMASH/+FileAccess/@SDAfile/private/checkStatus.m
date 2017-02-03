function varargout=checkStatus(archive)

status=struct;

info=h5info(archive.ArchiveFile,'/');
attributes=info.Attributes;
for n=1:numel(attributes)
    name=attributes(n).Name;
    value=attributes(n).Value;
    status.(name)=value;
end
status=orderfields(status);

if nargout==0
    disp(status);
else
    varargout{1}=status;
end

end