<template>
<div>
    <div v-if="isleaf" class="leaf">
        {{ label }} 
        <div v-if="!nodes.writable">
            <input v-if="nodes.type == 'boolean'" type="checkbox" v-model="outval"/>
            <input v-if="nodes.type == 'integer'" type="number" v-model.lazy="outval"/>
            <input v-if="nodes.type == 'string'" type="Text" v-model.lazy="outval"/>
        </div>
        <div v-else>
            <button v-on:click="get">GET</button>
        </div>
        <div class="disp">{{ value }}</div>
        
    </div>
    <div v-else class="node">
        <div>{{ label }}</div>
        <node 
            v-for="node in nodes" 
            :nodes="node.nodes" 
            :label="node.label"
            :key="node.id"
        >
        </node>
    </div>
</div>
</template>
<script>

export default { 
    props: [ 'label', 'nodes'],
    data() { return {outval: null} },
    name: 'node',
    computed:{
        isleaf() {
            return (this.nodes) ? this.nodes.type : false;
        },
        value(oldVal, newVal) {
            if (this.nodes){
                if (newVal == this.nodes.value){
                    return this.nodes.value
                }
                return newVal
            }
            return false
        }
    },
    created() {
        if ((this.nodes) && (this.nodes.type)){
            console.log(this.nodes.path + " created")
            this.$connect('ws://localhost:11111' + this.nodes.path)
            console.log(this.nodes.path + " connected")
            this.$options.sockets.onmessage = ({data}) => {
                let message = JSON.parse(data)
                if (message.path != this.nodes.path){
                    return
                }
                
                this.update(message.value);
            };
            console.log(this.nodes.path + " done")
        }
    },
    methods: {
        update(data) {
            this.nodes.value = data
        },
        get() {
            fetch(this.nodes.path)
            .then((response) => {
                return response.json()
            })
            .then((json) => {
                if (!this.nodes.readable){
                    this.nodes.value = json.data
                }
            })
        }
    },
    watch: {
        outval: async function (oldVal, newVal){
            if (newVal != oldVal){
                let out = (typeof this.outval != "string") ? this.outval : JSON.parse(this.outval)
                fetch(this.path, {
                    headers: { "Content-Type": "application/json; charset=utf-8" },
                    method: 'PATCH',
                    body: JSON.stringify({
                        op: 'replace',
                        path: this.nodes.path,
                        value: out
                    })
                })
                .then((response) => console.log(response))
            }
        }
    },
    destroyed() {
        this.$disconnect()
    }
}
</script>

<style scoped>
    .node{
        padding: 1em;
        letter-spacing:1px;
        font-family: 'Courier New', Courier, monospace;
        margin: 1em 0.5em;
        box-shadow: -3px 3px 8px 1px #181818;
        background-color: rgb(43, 43, 43);
        padding: 0.5em;
        color:#adadad;
        font-weight: bold;
    }
    .leaf{
        padding: 1em;
        letter-spacing:1px;
        font-family: 'Courier New', Courier, monospace;
        margin: 1em 0.5em;
        box-shadow: -3px 3px 8px 1px #181818;
        background-color: rgb(43, 43, 43);
        padding: 0.5em;
        color:#adadad;
        font-weight: bold;
    }
    .disp {
        color: white;
        font-weight: 900
    }
</style>
