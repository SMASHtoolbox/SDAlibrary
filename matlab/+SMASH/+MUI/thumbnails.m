function varargout=thumbnails(N)

% handle input
if (nargin<1) || isempty(N)
    N=3;
end
assert(N>1,'ERROR: at least two plots must be used');

haxes=nan(1,N);

% main axes
fig=figure;
height=0.80;
haxes(1)=axes('Units','normalize','OuterPosition',[0 1-height 1 height]);
setappdata(haxes(1),'Thumbnail',false);
setappdata(haxes(1),'Master',haxes(1));

% thumbnails
width=1/(N-1);
x0=0;
for n=2:N
    haxes(n)=axes('Units','normalize','OuterPosition',[x0 0 width 1-height]); %#ok<LAXES>
    x0=x0+width;
    setappdata(haxes(n),'Thumbnail',true);
    setappdata(haxes(n),'Master',haxes(1));
end

% manage swapping



set(fig,'WindowButtonDownFcn',@swapAxes)
    function swapAxes(varargin)
        target=get(fig,'CurrentAxes');
        thumbnail=getappdata(target,'Thumbnail');
        if isempty(thumbnail) || (~thumbnail)
            return
        end
        master=getappdata(target,'Master');
        pos1=get(master,'OuterPosition');
        pos2=get(target,'OuterPosition');
        set(master,'OuterPosition',pos2);
        setappdata(master,'Thumbnail',true);
        set(target,'OuterPosition',pos1);
        setappdata(target,'Thumbnail',false);
        for m=1:N
            setappdata(haxes(m),'Master',target);
        end
    end

% handle output
if (nargin==0) && (nargout==0)
    line('Parent',haxes(1));
    image('Parent',haxes(2));
    patch('Parent',haxes(3));
end

if nargout>0
    varargout{1}=haxes;
end

end