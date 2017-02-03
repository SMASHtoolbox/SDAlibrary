% view Display scan
%
% This method displays a LUNA scan as a line plot.
%     >> view(object);
%     >> h=view(object); % return graphic handle
% A new figure is created by default.
%
% Passing a graphic handle as the second input plots the scan in an
% existing figure/axes.
%     >> view(object,target);
% When target represents an axes, the scan is added and no other
% changes made.  When the target corresponds to a figure, the current axes
% is cleared before the scan is plotted.
%
% See also LUNA
%

%
% created April 29, 2015 by Daniel Dolan (Sandia National Laboratories)
%
function varargout=view(object,target)

% manage input
if (nargin<2) || isempty(target)
    fig=figure;
    target=axes('Box','on');
    newplot=true;
else
    switch get(target,'Type')
        case 'figure'
            fig=target;
            target=get(fig,'CurrentAxes');
            cla(target);
            newplot=true;
        case 'axes'
            fig=ancestor(target,'figure');
            newplot=false;
        otherwise
    end
end
assert(ishandle(target),'ERROR: invalid target handle');

% generate plot
h=line('Parent',target,'Color','k',...
    'XData',object.Time,'YData',object.LinearAmplitude);
if newplot
    xlabel('Transit time (ns)');
    ylabel('Linear return (1/mm)');
    set(gca,'YScale','log');
    if object.IsModified
        label=sprintf('Measurement file: %s (modified)',object.SourceFile);
    else
        label=sprintf('Measurement file: %s',object.SourceFile);
    end
    title(label,'Interpreter','none');
end

% manage output
if nargout==0
    figure(fig);
else
    varargout{1}=h;
end

end