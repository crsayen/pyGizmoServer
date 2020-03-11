import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import './static/styles.css'
import branchnode from './components/branchnode.vue'

Vue.use(BootstrapVue)

Vue.config.productionTip = false

function makenode(key, val, path){
    return {
        path: `${path}/${key}`,
        label: key,
        isleaf: false,
        nodes: parseschema(val, `${path}/${key}`)
    }
}
function makeleaf(key, val, path){
    return {
        path: `${path}/${key}`,
        label: key,
        type: val.$type,
        isleaf: true,
        readable: !!val.$read,
        writable: !!val.$write,
        streamable: !!val.$watchable
    }
}

function parseschema(item, path) {
    if (typeof item === "object" && item !== null){
        let nodes = []
        if (item.$count) {
            let count = item.$count
            delete item.$count
            let make = (item.$type) ? makeleaf : makenode
            for(let i = 0; i < count; i++){
                nodes.push(make(String(i), item, path))
            }
            return nodes
        }
        for (let [key, val] of Object.entries(item)){
            if (["$count", "controller", "wsurl"].includes(key)){
                continue
            }
            let make = (val.$type && !val.$count) ? makeleaf : makenode
            nodes.push(make(key, val, path));
        }
        return nodes
    }
}

fetch("/schema")
.then(async (response) => {
    let model = await response.json()
    let tree = new Object()
    tree.label = model.controller
    document.getElementById('head').innerText = tree.label
    tree.nodes = parseschema(model, '');
    console.log(tree)
    new Vue({
        el: '#app',
        data: {
            tree: tree,
            wsurl: model.wsurl
        },
        components: {
            branchnode
        }
    })
})
