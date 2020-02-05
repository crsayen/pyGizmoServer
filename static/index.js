
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

function parsetree(item, element){
    function append_stuff(txt,val,el){
        var div = document.createElement('div');
        div.className = "treenode"
        div.innerText = txt;
        el.appendChild(div);
        parsetree(val, div);
    }
    if (typeof item === "object" && item != null){
        for (const [key, val] of Object.entries(item)){
            if (key == "data"){
                parsetree(val, element);
                continue;
            }
            append_stuff(key,val,element);
        }
    }
    else if (Array.isArray(item)){
        for(i = 0; i < item.length; i++){
            append_stuff(String(i),item[i],element);
        }
    }
    else element.innerText = String(item);
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
                    parsetree(treejson, container);
                }
            );
            btn.className = "btn btn_selected";
        }else{
            btn.className = "btn";
        }
    });
}   








