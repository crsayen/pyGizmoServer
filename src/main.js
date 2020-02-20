import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import './static/styles.css'
import branchnode from './components/branchnode.vue'

Vue.use(BootstrapVue)

Vue.config.productionTip = false

function makenode(key, val, path){
    let obj = new Object();
    obj.path = path + '/' + key;
    obj.label = key;
    if(val.$type){
        obj.type = val.$type
        obj.isleaf = true
        obj.readable = (val.r) ? true : false
        obj.writable = (val.w) ? true : false
    }else{
        obj.isleaf = false
        obj.nodes = parseschema(val, obj.path);
    }
    return obj
}

function parseschema(item, path) {
    if (typeof item === "object" && item !== null){
        let nodes = []
        if (typeof(item.$count) == "number") {
            let count = item.$count
            delete item.$count
            for(let i = 0; i < count; i++){
                nodes.push(makenode(String(i), item, path))
            }
            return nodes
        }
        for (let [key, val] of Object.entries(item)){
            if (key == "$count" || key == "controller"){
                continue
            }
            nodes.push(makenode(key, val, path));
        }
        return nodes
    }
}

fetch("/schema")
.then(async (response) => {
    let model = await response.json()
    console.log(model)
    let tree = new Object()
    tree.label = model.controller
    tree.nodes = parseschema(model, '');
    new Vue({
        el: '#app',
        data: {
            tree
        },
        components: {
            branchnode
        }
    })
})