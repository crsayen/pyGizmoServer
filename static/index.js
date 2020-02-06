var treevisible = false;
var model_buttonbar = [];
var model;

function create_button_bar(roots){
    var btn_bar = document.createElement("div");
    btn_bar.id = "model_buttonbar";
    var m = document.getElementById("showModel");
    m.appendChild(btn_bar);
    roots.forEach((root, index, array) => {
        var btn = document.createElement('button');
        btn.className = "btn";
        btn.id = root;
        btn.innerText = root;
        model_buttonbar.push({root: root, button: btn});
        btn_bar.appendChild(btn);
    });
}

function append_stuff(txt,val,el, path){
    var div = document.createElement('div');
    div.className = "treenode"
    div.id = path
    div.innerText = txt;
    el.appendChild(div);
    parsetree(val, div, path + '/' + txt);
}

function groom(val){
    if (['','NULL','NONE'].includes(val.toUpperCase())){ return false; }
    if (["TRUE","FALSE","NULL"].includes(val.toUpperCase())){
        return val.toLowerCase();
    }
    else if(val !== null) {
        if(val.length > 0) {
            if (!isNaN(val)) {
                return val;
            }
        }
    }
    else if ((val) => val instanceof Array || val instanceof Object ? true : false) {
        return val;
    }else{
        return false;    
    }
}

function parsetree(item, element, path){
    if (typeof item === "object" && item !== null){
        for ([key, val] of Object.entries(item)){
            if (key == "data"){
                parsetree(val, element, path);
                continue;
            }
            append_stuff(String(key),val,element, path);
        }
    }
    else if (Array.isArray(item)){
        for(i = 0; i < item.length; i++){
            append_stuff(String(i),item[i],element, path);
        }
    }
    else{
        var e;
        if (String(item)[0] == '/'){
            e = document.createElement('dev');
            e.className = "treenode";
            e.innerHTML = String(item);
            e.id = path
        element.appendChild(e);
        }else{
            e = document.createElement('input');
            e.className = "treeinput"
            e.name = path.split('/').slice(-1)[0];
            e.value = String(item);
            e.id = path
            element.appendChild(e);
            var btn = document.createElement("button");
            btn.className = "submit";
            btn.textContent = "Submit";
            btn.addEventListener("click", () => {
                var input = document.getElementById(path).value;
                if (val = groom(input)){
                    val = JSON.parse(val);
                }else{
                    alert("invalid input: " + String(input));
                    return;
                }
                fetch(path, {
                    headers: { "Content-Type": "application/json; charset=utf-8" },
                    method: 'PATCH',
                    body: JSON.stringify({
                        op: 'replace',
                        path: path,
                        value: val
                    })
                })
            });
            element.appendChild(btn);
        } 
    }
}

function showtree(btn_root, roots){
    var container = document.getElementById("treecontainer");
    container.remove();
    roots.forEach((root, index, array) => {
        var btn = document.getElementById(root)
        if (root == btn_root){
            var m = document.getElementById("ui");
            var container = document.createElement('div');
            container.id = "treecontainer";
            m.appendChild(container);
            fetch(root)
                .then(async (response) => {
                    var treejson =  await response.json();
                    parsetree(treejson, container, '/' + btn_root);
                }
            );
            btn.className = "btn btn_selected";
        }else{
            btn.className = "btn";
        }
    });
}   







