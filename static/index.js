
function parsetree(item, element){
    function append_stuff(txt,val,el){
        var div = document.createElement('div');
        div.setAttribute('class','treenode');
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

function showTree(){
    var container = document.getElementById("indexMain")
    fetch("/relayController")
        .then(async (response) => {
            var treejson =  await response.json();
            parsetree(treejson, container);
        }
    )
}   








