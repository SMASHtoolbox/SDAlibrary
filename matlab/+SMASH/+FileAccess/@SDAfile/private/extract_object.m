function object=extract_object(archive,setname)

 temp=extract_structure(archive,setname);
 try
     ObjectClass=readAttribute(archive.ArchiveFile,setname,'Class'); % documented standard
 catch
     ObjectClass=readAttribute(archive.ArchiveFile,setname,'ClassName'); % undocumented alternative
 end
 object=structure2object(temp,ObjectClass);

end