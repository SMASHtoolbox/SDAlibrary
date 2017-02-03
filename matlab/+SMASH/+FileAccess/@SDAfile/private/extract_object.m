function object=extract_object(archive,setname)

 temp=extract_structure(archive,setname);
 try
     ObjectClass=h5readatt(archive.ArchiveFile,setname,'Class'); % documented standard
 catch
     ObjectClass=h5readatt(archive.ArchiveFile,setname,'ClassName'); % undocumented alternative
 end
 object=structure2object(temp,ObjectClass);

end