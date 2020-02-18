<template>
<div class="node">
    {{ label }} 
    <div v-if="writable">
        <input v-if="type == 'boolean'" type="checkbox" v-model="outValue"/>
        <input v-else-if="type == 'integer'" type="number" v-model.lazy="outValue"/>
        <input v-else type="Text" v-model.lazy="outValue"/>
    </div>
    <div v-if="readable">
        <button @click="get"
        v-text="get"
        class="btn"
        :disabled="watching"
        :class="{disabled: watching}"
        ></button>
    </div>
    <div v-if="watchable">
        <button 
        class='btn' 
        type="button" 
        @click="watch_unwatch" 
        v-text="watching ? watch : watching"
        :class="{active: !watching}"
    ></button>
    </div>
    <div class="disp">{{ value }}</div>
</div>
</template>


<script>
const ws = require('isomorphic-ws')

export default {
    props: [ 'label', 'type', "writable", "readable", "path"],
    data() { 
        return {
            outValue: null,
            value: null,
            ws: null,
            watching: false
        } 
    },
    name: 'LeafNode',
    methods: {
        update(data) {
            this.value = data
        },
        get() {
            fetch(this.path)
            .then((response) => {
                return response.json()
            })
            .then((json) => {
                if (!this.readable){
                    this.value = json.data
                }
            })
        },
        watch_unwatch() {
            if (this.watching) {
                this.ws = new ws(this.$shared.wspath + this.path)
                this.ws.onmessage = (data) => this.value = data.value
                this.watching = true
            }
        }
    },
    watch: {
        outValue: (oldVal, newVal) => {
            if (newVal != oldVal){
                // everything gets turned to strings unless I parse it now
                if (typeof newVal != "string") { newVal = JSON.parse(newVal)}
                this.$shared.patchReplace(this.path, newVal)
                .then((response) => response.json())
                .then((res) => (this.watching) ? this.value : res.data)
            }
        }
    },
    destroyed() {
        this.ws.destroy()
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
        color:#adadad;		/* I'm not sure what "rgb(241, 237, 231)" is, but I'm not using it ( too much contrast ) . */
        font-weight: bold;
    }
    .btn {
        background: #565656;
    }
    .active {
        background: #457e55;
    }
    .disabled {
        background: #7f7f7f;
        color: #646464;
    }
    .disp {
        color: white;
        font-weight: 900;
    }
</style>