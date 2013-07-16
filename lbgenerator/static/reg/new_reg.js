function include_js(filename)
{
    var head = document.getElementsByTagName('head')[0];

    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';

    head.appendChild(script)
}

function include_css(filename)
{
    var head = document.getElementsByTagName('head')[0];

    var script = document.createElement('link');
    script.href = filename;
    script.type = 'text/css';
    script.rel = 'stylesheet'

    head.appendChild(script)
}

if (window.location.pathname.split('/')[4] != 'full'){

    var js = '/static/reg/custom_form.js';
    var css = '/static/ext-4.1.1a/resources/css/ext-all.css';
    include_js(js)
    include_css(css)
}
else{

    var js = '/static/reg/full_form.js';
    include_js(js)
}
