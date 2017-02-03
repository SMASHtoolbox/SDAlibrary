function datacursor(object,mode)

switch mode
    case 'create'
        h=uitoggletool('Parent',object.ToolBar,...
            'Tag','DataCursor','ToolTipString','Data cursor',...
            'Cdata',local_graphic('DatatipIcon'),'Separator','off',...
            'ClickedCallback',@callback);
        object.ToolButton.DataCursor=h;
    case 'hide'
        set(object.Button.DataCursor,'Visible','off');
    case 'show'
        set(object.Button.DataCursor,'Visible','on');
end

%%
    function callback(src,varargin)
        state=get(src,'State');
        detoggle(object);
        if strcmpi(state,'on')
            set(src,'State','on');
            dcm_obj=datacursormode(object.Handle);
        set(dcm_obj,'Enable','on','UpdateFcn',@datacursor_text)
        end
    end

end


%%
function output_txt = datacursor_text(obj,event_obj)
% Display the position of the data cursor
% obj          Currently not used (empty)
% event_obj    Handle to event object
% output_txt   Data cursor text string (string or cell array of strings).


pos = get(event_obj,'Position');
x=pos(1);
output_txt{1}=sprintf('X: %#+.6g',x);
y=pos(2);
output_txt{2}=sprintf('Y: %#+.6g',y);

target=get(event_obj,'Target');
switch get(target,'Type')
    case 'image'
        zdata=get(target,'CData');
        [M,N]=size(zdata);        
        xdata=get(target,'XData');
        xdata=linspace(xdata(1),xdata(end),N);
        ydata=get(target,'YData');
        ydata=linspace(ydata(1),ydata(end),M);
        z=interp2(xdata,ydata,zdata,x,y,'nearest');
    output_txt{3}=sprintf('Z: %#+.6g',z);
end

end