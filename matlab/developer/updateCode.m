% This function pulls code from the SMASH toolbox into the matlab directory
% of SDAlibrary

function updateCode()

destination=mfilename('fullpath');
destination=fileparts(fileparts(destination));

loadSMASH -program SDAbrowser
source=which('SDAbrowser');

SMASH.System.deploy(source,destination);

if ispc
    winopen(destination);
elseif ismac
    system(sprintf('open %s',destination));
end

end