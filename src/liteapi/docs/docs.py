from ..BaseAPIRequest import BaseAPIRequest
from ..APIModel import APIModel
from .annotate import isAnnotate
from .._internals import _repr, _isUnion
from ..verifiers.verifiers import isVerifierClass

_DOCS_CSS='''body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif}.nodisplay{display:none !important}.api{padding-inline-end:40px}.api>li{list-style-type:none}.api>li.delete>.header{background-color:#f5e8e8;border:1px solid #e8c6c7}.api>li.get>.header{background-color:#e7f0f7;border:1px solid #c3d9ec}.api>li.head>.header{background-color:#fcffcd;border:1px solid #ffd20f}.api>li.patch>.header{background-color:#fce9e3;border:1px solid #f5d5c3}.api>li.post>.header{background-color:#e7f6ec;border:1px solid #c3e8d1}.api>li.put>.header{background-color:#f9f2e9;border:1px solid #f0e0ca}.api>li>.header .breif{display:inline-end;text-align:right;margin-top:3px;margin-right:10px;float:right;font-size:.8em}.api>li>.header .operation::before{display:inline-block;text-transform:uppercase;color:#fff;font-size:.7em;font-weight:bold;text-align:center;padding:7px 0 4px;border-radius:2px;width:50px;margin-right:10px}.api>li.delete>.header .operation::before{content:"DELETE";background-color:#a41e22}.api>li.get>.header .operation::before{content:"GET";background-color:#0f6ab4}.api>li.head>.header .operation::before{content:"HEAD";background-color:#ffd20f}.api>li.patch>.header .operation::before{content:"PATCH";background-color:#d38042}.api>li.post>.header .operation::before{content:"POST";background-color:#09602a}.api>li.put>.header .operation::before{content:"PUT";background-color:#604114}.api>li>.body{padding:10px;margin-bottom:20px;border-top:0 !important;border-bottom-left-radius:5px;border-bottom-right-radius:5px}.api>li>.body pre{background-color:#fcf6db;border:1px solid #e5e0c6;font-family:'Courier New',Courier,monospace;padding:.5em;display:block}.api>li>.body pre code{line-height:1.6em}.api>li.delete>.body{background-color:#f7eded;border:1px solid #e8c6c7}.api>li.get>.body{background-color:#ebf3f9;border:1px solid #c3d9ec}.api>li.head>.body{background-color:#fcffcd;border:1px solid #ffd20f}.api>li.patch>.body{background-color:#faf0ef;border:1px solid #f5d5c3}.api>li.post>.body{background-color:#ebf7f0;border:1px solid #c3e8d1}.api>li.put>.body{background-color:#faf5ee;border:1px solid #f0e0ca}.api>li.delete>.header .breif,.api>li.delete>.body .title{color:#a41e22}.api>li.get>.header .breif,.api>li.get>.body .title{color:#0f6ab4}.api>li.head>.header .breif,.api>li.head>.body .title{color:#ffd20f}.api>li.patch>.header .breif,.api>li.patch>.body .title{color:#d38042}.api>li.post>.header .breif,.api>li.post>.body .title{color:#09602a}.api>li.put>.header .breif,.api>li.put>.body .title{color:#604114}.api .body .title{margin:0;font-size:1.1em;padding:15px 0 5px}.api .body .authorization{float:right;margin:15px 0 10px}.api .body .authorization .auth_btn{cursor:pointer;height:18px;width:18px;vertical-align:middle;display:inline-block}.api .body .authorization .auth_btn_logout{background:url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48IS0tISBGb250IEF3ZXNvbWUgUHJvIDYuMi4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlIChDb21tZXJjaWFsIExpY2Vuc2UpIENvcHlyaWdodCAyMDIyIEZvbnRpY29ucywgSW5jLiAtLT48cGF0aCBmaWxsPSIjZDIyYjJiIiBkPSJNMTQ0IDE0NHY0OEgzMDRWMTQ0YzAtNDQuMi0zNS44LTgwLTgwLTgwcy04MCAzNS44LTgwIDgwek04MCAxOTJWMTQ0QzgwIDY0LjUgMTQ0LjUgMCAyMjQgMHMxNDQgNjQuNSAxNDQgMTQ0djQ4aDE2YzM1LjMgMCA2NCAyOC43IDY0IDY0VjQ0OGMwIDM1LjMtMjguNyA2NC02NCA2NEg2NGMtMzUuMyAwLTY0LTI4LjctNjQtNjRWMjU2YzAtMzUuMyAyOC43LTY0IDY0LTY0SDgweiIvPjwvc3ZnPg==) no-repeat}.api .body .authorization .auth_btn_login{background:url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48IS0tISBGb250IEF3ZXNvbWUgUHJvIDYuMi4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlIChDb21tZXJjaWFsIExpY2Vuc2UpIENvcHlyaWdodCAyMDIyIEZvbnRpY29ucywgSW5jLiAtLT48cGF0aCBmaWxsPSIjMDA4MDAwIiBkPSJNMTQ0IDE0NGMwLTQ0LjIgMzUuOC04MCA4MC04MGMzMS45IDAgNTkuNCAxOC42IDcyLjMgNDUuN2M3LjYgMTYgMjYuNyAyMi44IDQyLjYgMTUuMnMyMi44LTI2LjcgMTUuMi00Mi42QzMzMSAzMy43IDI4MS41IDAgMjI0IDBDMTQ0LjUgMCA4MCA2NC41IDgwIDE0NHY0OEg2NGMtMzUuMyAwLTY0IDI4LjctNjQgNjRWNDQ4YzAgMzUuMyAyOC43IDY0IDY0IDY0SDM4NGMzNS4zIDAgNjQtMjguNyA2NC02NFYyNTZjMC0zNS4zLTI4LjctNjQtNjQtNjRIMTQ0VjE0NHoiLz48L3N2Zz4=) no-repeat}.api .body .nav{display:block;min-width:230px;margin:5px 0 0 0;padding:0;list-style:none}.api .body .nav>li{float:left;margin:0 5px 5px 0;padding:2px 5px 5px 0}.api .body .nav>li:not(:last-child){border-right:1px solid #ddd}.api .body .nav a{color:#505050;text-decoration:none}.api .body .nav a:hover{text-decoration:underline}.api .body .nav .selected{color:black;text-decoration:none}.api .body .container{clear:both}.api .body .descriptor>div{max-height:150px;overflow:auto;font-size:0.8em;white-space:nowrap}.api .body pre{overflow:auto;max-height:150px}.api .body code{color:#444}.api .body code .value{color:#800}.api .sandbox table{width:100%;border-collapse:collapse}.api .sandbox table th{font-weight:normal;color:#505050;border-bottom:2px solid black}.api .sandbox table td{border-top:1px solid #505050}.api .sandbox table td:nth-child(1){font-family:'Courier New',Courier,monospace;font-weight:1000;font-size:.9em;width:10%}.api .sandbox table td:nth-child(3){font-size:0.8em;width:20%}.api .sandbox table td:nth-child(4){width:40%}.api .sandbox .parameters td{font-weight:500}.api .sandbox .parameters td input,.api .sandbox .parameters td textarea{width:90%}.api .sandbox .parameters td textarea{resize:vertical;min-height:100px}.api .sandbox .tryout button{padding:6px 8px}.api .sandbox .tryout .response_hider{font-size:.9em}'''
_DOC_JS='''document.querySelectorAll(".api .body .nav a").forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();let myNav=this.closest(".nav");let myContainer=myNav.nextElementSibling;let myIndex=Array.prototype.indexOf.call(myNav.children,this.closest("li"));this.classList.add("selected");myNav.children[+!myIndex].firstChild.classList.remove("selected");myContainer.children[myIndex].classList.remove("nodisplay");myContainer.children[+!myIndex].classList.add("nodisplay");return false})});document.querySelectorAll(".api .body .tryout button").forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();let body=this.closest(".body");/*body.querySelector(".response").classList.remove("nodisplay");this.parentNode.querySelector(".response_hider").classList.remove("nodisplay");*/alert("Under development!");return false})});document.querySelectorAll(".api .body .tryout .response_hider").forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();let body=this.closest(".body");body.querySelector(".response").classList.add("nodisplay");this.classList.add("nodisplay");return false})});'''

class _infoClass(BaseAPIRequest):
    _hasDoc = False
    def get(self):
        return self.app._liteapi__docs._docs__info

class _maincss(BaseAPIRequest):
    _hasDoc = False
    def get(self):
        self.response['Content-Type'] = 'text/css; charset=utf-8'
        self.response['Cache-Control'] = 'no-store'
        return _DOCS_CSS

class _mainjs(BaseAPIRequest):
    _hasDoc = False
    def get(self):
        self.response['Content-Type'] = 'text/javascript; charset=utf-8'
        self.response['Cache-Control'] = 'no-store'
        return _DOC_JS

class _docClass(BaseAPIRequest):
    _hasDoc = False
    def get(self):
        self.response['Content-Type'] = 'text/html; charset=utf-8'
        self.response['Cache-Control'] = 'no-store'
        return self.app._liteapi__docs._docs__doc

class _docs:
    def __init__(self, app):
        self.__app = app
        self.__info = []
        self.__doc = '<!DOCTYPE html><html><head><title>REST API Documentation</title>\
<link rel="stylesheet" href="doc/css/main.css"></head><body>'
        
        app.register('/info')(_infoClass)
        app.register('/doc/css/main.css')(_maincss)
        app.register('/doc/script/main.js')(_mainjs)
        app.register('/doc')(_docClass)
    
    def build(self):
        print("Building REST API Documentation page...")
        for regex in self.__app._liteapi__request:
            if self.__app._liteapi__request[regex]._hasDoc:
                self.__info.append({'uri': self.__app._liteapi__request[regex]._BaseAPIRequest__definition, 'methods': self.__app._liteapi__request[regex]._BaseAPIRequest__methods_keys})
                self.__doc += self.__addMethods(self.__app._liteapi__request[regex])
        self.__doc += '<script src="doc/script/main.js"></script></body></html>'
        print("""Documentation building completed:
        http{}://{}:{}/doc""".format('s' if self.__app._liteapi__ssl else '', self.__app._liteapi__config['host'], self.__app._liteapi__config['port']))

    def __getDescription(self, method):
        if not method.__doc__:
            return ''
        return f'<h4 class="title">Description</h4><div>{method.__doc__}</div>'

    def __getAuthorization(self, method):
        if not method.authenticator:
            return ''
        return f'<div class="authorization"><div class="auth_btn auth_btn_logout" authtype="{method.authenticator.__name__}"></div></div>'

    def __getClass(self, cls):
        classList = [cls]
        i = 0
        out = ''
        while True:
            if i >= len(classList):
                break
            c = classList[i]
            i += 1
            out += f'class {_repr(c)} {{<br>'
            for key in c.__annotations__:
                annotation = c.__annotations__[key]
                out += f'&emsp;{key}; //({_repr(annotation)})'
                if isAnnotate(annotation):
                    if annotation.doc:
                        out += f' {annotation.doc}'
                    annotation = annotation.cls
                out += '<br>'
                if isinstance(annotation, type) and issubclass(annotation, APIModel) and annotation not in classList:
                    classList.append(annotation)
                elif _isUnion(annotation):
                    for a in annotation.__args__:
                        if isinstance(a, type) and issubclass(a, APIModel) and a not in classList:
                            classList.append(a)
            out += '}<br><br>'
        return out
    
    def __getClassExample(self, cls, sp = 4, level = 0):
        out = []
        indent = ' ' * (sp * level)
        contentIndent = ' ' * (sp * (level + 1))
        for key in cls.__annotations__:
            annotation = cls.__annotations__[key]
            example = ''
            if isAnnotate(annotation):
                if annotation.example != '' and isinstance(annotation.example, (str, int, float, bool)):
                    example = annotation.example
                annotation = annotation.cls if not isVerifierClass(annotation.cls) else type(annotation.example or None)
            if _isUnion(annotation):
                if type(None) in annotation.__args__ and example == '':
                    continue
                annotation = type(example) if example != '' else annotation.__args__[0]
            out2 = f'"{key}": '
            if annotation in (int, float, bool):
                out2 += f'<span class="value">{example or "..."}</span>'.lower()
            elif annotation is str:
                out2 += f'<span class="value">"{example or "..."}"</span>'
            elif annotation in (list, tuple):
                out2 += f'[{example or "..."}]'
            elif annotation is dict:
                out2 += f'{{{example or "..."}}}'
            elif isinstance(annotation, type) and issubclass(annotation, APIModel):
                out2 += self.__getClassExample(annotation, sp = sp, level = level + 1)
            else:
                out2 += f'<span class="value">{example or "..."}</span>'
            out.append(out2)
        example = f',<br>{contentIndent}'.join(out)
        return f'{{<br>{contentIndent}{example}<br>{indent}}}'
    
    def __addClass(self, cls):
        descriptiors = self.__getClass(cls)
        example = self.__getClassExample(cls)
        classStr = f'<ul class="nav"><li><a href="#">Model</a></li><li><a href="#" class="selected">Example</a></li></ul>\
<div class="container"><div class="descriptor nodisplay"><div>{descriptiors}</div></div>\
<div class="example"><pre><code>{example}</code></pre></div></div>'
        return classStr
    
    def __getResponseClass(self, method):
        response = f'<div class="response_class">'
        for r in method.responses:
            response += f'<h4 class="title">Response Code({r[0]})</h4><div>{r[1]}</div>'
            if len(r) == 3:
                response += f'{self.__addClass(r[2])}'
        return f'{response}</div>'

    def __addParameters(self, procedure):
        parameters = procedure.args
        if not len(parameters):
            return ''
        params = '<h4 class="title">Parameters</h4><table class="parameters"><thead><tr><th>Parameter</th><th>Value</th><th>Description</th><th>Data Type</th></tr></thead><tbody>'
        for param in parameters:
            description = parameters[param].doc if isAnnotate(parameters[param]) else ''
            value = parameters[param].example if isAnnotate(parameters[param]) else ''
            params += f'<tr><td>{param}</td>'
            if isinstance(parameters[param], type) and issubclass(parameters[param], APIModel):
                params += f'<td><textarea id="{param}"></textarea></td><td>{description}</td><td>{self.__addClass(parameters[param])}</td>'
            else:
                params += f'<td><input type="text" id="{param}" value="{value}"></td><td>{description}</td><td>{_repr(parameters[param])}</td>'
            params += '</tr>'
        params += '</tbody></table>'
        return params

    def __addMethods(self, cls):
        methods_doc = ''
        for method_name in cls._BaseAPIRequest__methods_keys:
            method = cls._BaseAPIRequest__methods[method_name]
            values = {
                'METHOD': method_name.lower(),
                'PATH': cls._BaseAPIRequest__definition,
                'BREIF': method.description or '',
                'DESCRIPTION': self.__getDescription(method),
                'AUTHORIZATION': self.__getAuthorization(method),
                'RESPONSE_CLASS': self.__getResponseClass(method),
                'PARAMETERS': self.__addParameters(method)
            }
            methods_doc += '<ul class="api"><li class="{METHOD}"><div class="header"><span class="operation">{PATH}</span>\
<span class="breif">{BREIF}</span></div><div class="body">{DESCRIPTION}{AUTHORIZATION}{RESPONSE_CLASS}<form class="sandbox">\
{PARAMETERS}<div class="tryout"><button type="submit">Try it out!</button><a href="#" class="response_hider title nodisplay">Hide Response</a>\
<span class="progressbar nodisplay"></span></div></form><div class="response nodisplay"><h4 class="title">Curl</h4>\
<pre class="curl"><code></code></pre><h4 class="title">Response Body</h4><pre class="body"><code></code></pre>\
<h4 class="title">Response Code</h4><pre class="code"><code></code></pre><h4 class="title">Response Headers</h4>\
<pre class="headers"><code></code></pre></div></div></li></ul>'.format(**values)
        return methods_doc