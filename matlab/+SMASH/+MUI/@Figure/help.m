function help(object,mode)

switch mode
    case 'create'
        h=uitoggletool('Parent',object.ToolBar,...
            'Tag','Help','ToolTipString','Toolbar help',...
            'Cdata',local_graphic('HelpIcon'),'Separator','off',...
            'ClickedCallback',@callback);
        object.ToolButton.help=h;
    case 'hide'
        set(object.Button.help,'Visible','off');
    case 'show'
        set(object.Button.help,'Visible','on');
end

end

%%
function callback(varargin)
% create message
indent=repmat(' ',[1 5]);
indent=[indent '-'];
message={};
message{end+1}='Toolbar operations';
message{end+1}=' ';
message{end+1}='Set working directory:';
message{end+1}=[indent ...
    'Change the current directory using a dialog box.'];
message{end+1}=' ';
message{end+1}='Export figure:';
message{end+1}=[indent...
    'Export figure to a graphic file (*.eps, *.jpg, *.pdf, *.png, or *.tif).'];
message{end+1}=' ';
message{end+1}='Zoom:';
message{end+1}=[indent 'Zoom in with mouse click or click and drag.'];
message{end+1}=[indent 'Zoom out with shift-click; double-click to restore original view.'];
message{end+1}=[indent 'Press right mouse button (control-click) for additional options.'];
message{end+1}=' ';
message{end+1}='Pan:';
message{end+1}=[indent 'Click and drag to pan over an axes; double-click to restore original view.'];
message{end+1}=[indent 'Press right mouse button (control-click) for additional options.'];
message{end+1}=' ';
message{end+1}='Auto scale:';
message{end+1}=[indent 'Click on axes to set nice limits.'];
message{end+1}=[indent 'Shift-click to auto scale all figure axes.'];
message{end+1}=' ';
message{end+1}='Tight scale:';
message{end+1}=[indent 'Click on axes to set tight limit'];
message{end+1}=[indent 'Shift-click to tight scale all figure axes.'];
message{end+1}=' ';
message{end+1}='Manual scale:';
message{end+1}=[indent 'Click on axes to manually set limits.'];
message{end+1}=' ';
message{end+1}='Data cursor:';
message{end+1}=[indent 'Click on data to display (x,y,z) coordinates.'];
message{end+1}=[indent 'Press right mouse button (control-click) for additional options.'];
message{end+1}=' ';
message{end+1}='Region of interest (ROI) statistics:';
message{end+1}=[indent 'Click and drag to specify a region of interest.'];
message{end+1}=[indent 'Local statistics in this region will be displayed.'];
message{end+1}=' ';
message{end+1}='Overlay (x,y) data:';
message{end+1}=[indent 'Click on axes to overlay (x,y) data from a file.'];
message{end+1}=[indent 'Right-click overlays to make adjustments.'];
message{end+1}=' ';
message{end+1}='Slice image:';
message{end+1}=[indent 'Click on image to generate horizontal and vertical slice plots. '];
message{end+1}=' ';
message{end+1}='Clone axes:';
message{end+1}=[indent 'Click on axes to clone to another figure.'];
message{end+1}=' ';
message{end+1}='Standard toolbar:';
message{end+1}=[indent 'Show/hide standard figure toolbar.'];
message{end+1}=' ';
numlines=numel(message);
width=0;
for ii=1:numlines
    width=max([width numel(message{ii})]);
end
% create dialog
fig=findall(0,'Type','figure','Tag','MinimalFigure:Help');
if ishandle(fig)
    delete(fig);
end
fig=figure('Toolbar','none','Menubar','none','DockControls','off',...
    'Tag','MinimalFigure:Help','Visible','off',...
    'Units','characters','Resize','off',...
    'IntegerHandle','off','HandleVisibility','callback',...
    'NumberTitle','off','Name','Toolbar help');

gset=GUIsettings;
htext=uicontrol('Style','text',...
    'Units','characters','Position',[0 0 80 1],...
    'HorizontalAlignment','left',...
    'Max',2,'Min',0,'BackgroundColor',gset.textbgcolor);
[message,pos]=textwrap(htext,message);
figpos=[0 0 pos(3)+2*gset.hmargin pos(4)+2*gset.vmargin];

pos(1)=pos(1)+gset.hmargin;
pos(2)=pos(2)+gset.vmargin;
set(htext,'String',message,'Position',pos);

set(fig,'Position',figpos);
movegui(fig,'center');
set(fig,'Visible','on');

setappdata(fig,'SourceFigure',gcbf);

end

%%
function func=GUIsettings(field)

% input handling
if nargin<1
    field='';
end
if isempty(field)
    field='all';
end
% GUI parameters
persistent param
if isempty(param) % character units
    param.hmargin=1;
    param.vmargin=1;
    param.textheight=1.5;
    param.buttonheight=2;
    %param.controlheight=1.5;
    param.buttonwidth=8; % small button (OK, etc.)
    param.editwidth=15;
    param.labelwidth=4; % small label
    param.checkwidth=10;
    param.fontname='fixed';
    param.textbgcolor=get(0,'DefaultFigureColor');
    param.editcolor=[1 1 1];
end
% output control
field=lower(field);
if strcmp(field,'all')
    func=param;
elseif isfield(param,field)
    func=param.(field);
else
    error('Invalid GUIsettings field');
end

end