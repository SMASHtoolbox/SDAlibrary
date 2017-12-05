function FullName=resolveName(package,name)

if name(1)=='.'
    name=name(2:end);
end

errmsg='ERROR: invalid package name';

object=meta.package.fromName(package);
while true
    index=strfind(name,'.');
    if isempty(index)
        ShortName=name;
        FullName=sprintf('%s.%s',object.Name,name);
        break           
    elseif name(1)=='-'
        object=meta.package.fromName(object.ContainingPackage.Name);
        name=name(3:end);
    else
        sub=name(1:(index(1)-1));
        sub=sprintf('%s.%s',object.Name,sub);
        object=meta.package.fromName(sub);
        assert(~isempty(object),errmsg);
        name=name(index(1)+1:end);
    end       
end

% verify name
for n=1:numel(object.FunctionList)
    if strcmp(object.FunctionList(n).Name,ShortName)
        return
    end
end

for n=1:numel(object.ClassList)
    if strcmp(object.ClassList(n).Name,FullName)
        return
    end
end

error('ERROR: requested function/class not found');

end