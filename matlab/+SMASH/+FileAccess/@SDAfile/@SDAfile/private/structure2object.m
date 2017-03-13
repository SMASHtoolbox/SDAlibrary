function object=structure2object(data,ClassName)

try % pass structure to (static) restore method
    name=sprintf('%s.restore',ClassName);
    object=feval(name,data);
    return
catch
    % onward...
end

try % create empty object and transfer properties
    object=feval(ClassName);
    temp=metaclass(object);
    name=temp.PropertyList;
    problem=false;
    for k=1:numel(name)        
        try
            object.(name(k).Name)=data.(name(k).Name);
        catch
            switch name(k).Name
                case 'UnderlyingObj'
                    continue
                otherwise
                    problem=true;
            end            
        end
    end
    if problem
        message={};
        message{end+1}=sprintf('The "%s" class does not provide a restore method.',ClassName);
        message{end+1}='   -Private and protected data were not transferred';
        message{end+1}='   -Restored object may behave in unexpected ways.';
        warning('SDA:restore','%s\n',message{:});
    end
    return
catch
    % onward...
end

message={};
message{end+1}='Unable to recreate stored object';
message{end+1}='Returning data as a structure';
warning('SDA:restore','%s\n',message{:});
object=data;


end