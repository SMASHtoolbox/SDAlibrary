% This class creates objects for displaying and analyzing fiber scans from
% a LUNA optical backscatter reflectomer.  LUNA objects are created from a
% source file:
%     >> object=LUNA(filename);
% Binary (*.obr) and text files are both accepted.  If no file is
% specified, the user is prompted to select one.
%
% LUNA objects allow fiber scans to be:
%     -displayed (view method)
%     -transferred to a custom time axes (modify method)
%     -analyzed for peaks (locate method).
%     -stored in a compact, portable file (store method)
% Refer to the specific methods for more information.
%
% See also Velocimetry
%

%
% created April 29, 2015 by Daniel Dolan (Sandia National Laboratories)
%
classdef LUNA
    properties (SetAccess=protected)     
        SourceFile % LUNA scan file
        FileHeader % Scan file header
        IsModified % Logical indicator of modified time axes 
        Time % Transit time [nanoseconds]     
        LinearAmplitude % Fractional signal per unit length [1/millmeters]
    end
       %TimeMode = 'RoundTrip' % Timing mode: 'SinglePass' or 'RoundTrip'
    %%
    methods (Hidden=true)
        function object=LUNA(filename)
            if nargin<1
                filename='';
            elseif strcmp(filename,'-empty') % empty object
                return
            end
            object=read(object,filename);
        end
        varargout=read(varargin);
    end    
    methods (Static=true, Hidden=true)
        varargout=restore(varargin);
    end
end