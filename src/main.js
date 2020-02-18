import Vue from 'vue'
import BranchNode from './components/BranchNode.vue'


Vue.config.productionTip = false

function makenode(key, val, path){
    let obj = new Object();
    obj.path = path + '/' + key;
    obj.label = key;
    obj.isleaf = false
    obj.nodes = parsetree(val, obj.path);
    return obj
}

function smakenode(key, val, path){
    let obj = new Object();
    obj.path = path + '/' + key;
    obj.label = key;
    obj.isleaf = false
    obj.nodes = parseschema(val, obj.path);
    return obj
}

function parsetree(item, path) {
    if (typeof item === "object" && item !== null){
        let nodes = [];
        for (let [key, val] of Object.entries(item)){
            nodes.push(makenode(key, val, path));
        }
        return nodes
    }
    else if (Array.isArray(item)) {
        return item.map((value, index) => makenode(String(index), value, path))
    }
    else{
        let obj = new Object();
        obj.label = '';
        obj.path = path;
        obj.value = item;
        obj.isleaf = false
        obj.type = String(typeof item);
        return obj;
    }
}

function parseschema(item, path) {
    if (typeof item === "object" && item !== null){
        let nodes = []
        if (typeof(item.$count) == "number") {
            let count = item.$count
            delete item.$count
            for(let i = 0; i < count; i++){
                nodes.push(smakenode(String(i), item, path))
            }
            return nodes
        }
        else if(item.$type){
            let obj = new Object()
            obj.label = ''
            obj.path = path
            obj.value = "unknown"
            obj.type = item.$type
            obj.isleaf = true
            obj.readable = (item.r) ? false : true
            obj.writable = (item.w) ? false : true
            return obj
        }
        for (let [key, val] of Object.entries(item)){
            if (key == "$count"){
                continue
            }
            nodes.push(smakenode(key, val, path));
        }
        return nodes
    }
}

function patchReplace(path, value){
    return fetch(
        path, {
            headers: { "Content-Type": "application/json; charset=utf-8" },
            method: 'PATCH',
            body: JSON.stringify({
                op: 'replace',
                path: path,
                value: value
            })
        }
    )}

const shared = {
    wspath: 'ws://localhost:11111',
    patchReplace: patchReplace
}

shared.install = function(){
    Object.defineProperty(Vue.prototype, '$shared', {
        get () { return shared }
    })
}

Vue.use(shared);

fetch("/schema")
.then(async (response) => {
    let model = await response.json()
    let tree = new Object()
    tree.label = model.controller
    tree.nodes = parseschema(model, '');
    new Vue({
        el: '#app',
        data: {
            tree
        },
        components: {
            BranchNode
        }
    })
})