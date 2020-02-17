import Vue from 'vue'
import Node from './components/node.vue'
import VueNativeSock from 'vue-native-websocket'

Vue.config.productionTip = false

/* This is temporary data, in reality this will be fetched */
// let data = {
//   relayController:{
//     relays: [
//       {enabled: true},
//       {enabled: false},
//     ]
//   },
//   pwmController: {
//     pwmMonitorUpdateRate: 100,
//     bankA: {
//       frequency: 1000
//     },
//     bankB: {
//       frequency: 1234
//     },
//     pwms: [
//       {
//         enabled: false,
//         dutyCycle: 50
//       },
//       {
//         enabled: false,
//         dutyCycle: 50
//       },
//     ]
//   }
// }


function makenode(key, val, path){
    let obj = new Object();
    obj.path = path + '/' + key;
    obj.label = key;
    obj.nodes = parsetree(val, obj.path);
    return obj
}

function smakenode(key, val, path){
    let obj = new Object();
    obj.path = path + '/' + key;
    obj.label = key;
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
            console.log("type")
            let obj = new Object()
            obj.label = ''
            obj.path = path
            obj.value = "unknown"
            obj.type = item.$type
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

Vue.use(VueNativeSock, 'ws://localhost:11111/', {
  connectManually: true,
})

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
            Node
        }
    })
})