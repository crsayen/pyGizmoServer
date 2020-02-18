<template>
    <div class="leaf node">
        <div class="disp">
            {{ label }}: 
            <div class="value">
                {{ value }}
            </div>
        </div>
        <div v-if="writable" class="inp">
            <input v-if="type == 'boolean'" type="checkbox" v-model="outValue"/>
            <input v-else-if="type == 'integer'" type="number" v-model.lazy="outValue"/>
            <input v-else type="Text" v-model.lazy="outValue"/>
        </div>
        <div class="btnBox">
            <div v-if="readable">
                    <button @click="get"
                    class="getBtn"
                    :disabled="watching"
                    :class="{enabled: !watching, disabled: watching}"
                >GET</button>
            </div>
            <div v-if="true">
                <button
                    class="watchBtn"
                    type="button"
                    @click="watch_unwatch" 
                    v-text="watching ? 'WATCHING' : 'WATCH'"
                    :class="{on: watching, off: !watching}"
                ></button>
            </div>
        </div>
    </div>
</template>


<script>
const ws = require('isomorphic-ws')

export default {
    props: [ 'label', 'type', "writable", "readable", "path"],
    data() { 
        return {
            outValue: null,
            value: "unknown",
            ws: null,
            watching: false
        } 
    },
    name: 'leafnode',
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
                if (!this.watching){
                    console.log(json)
                    this.value = json[0].data
                }
            })
        },
        patch(value) {
            fetch(this.path, { headers: { 
                    "Content-Type": "application/json; charset=utf-8" 
                },
                method: 'PATCH',
                body: JSON.stringify({
                    op: 'replace',
                    path: this.path,
                    value: value
                })
            })
            .then((response) => response.json())
            .then((res) => {
                if (!this.watching) {
                    this.value = res[0].data
                }
            }
        )},
        watch_unwatch() {
            if (!this.watching) {
                this.ws = new ws('ws://localhost:11111' + this.path)
                this.ws.onmessage = (data) => this.value = JSON.parse(data.data).value
                this.watching = true
            }else{
                this.ws.close()
                this.ws = null
                this.watching = false
            }
        }
    },
    watch: {
        outValue: function(newVal, oldVal) {
            if (newVal != oldVal){
                // everything gets turned to strings unless I parse it now
                if (typeof newVal != "string") { newVal = JSON.parse(newVal)}
                this.patch(newVal)
            }
        }
    },
    destroyed() {
        if (this.ws !== null){
            this.ws.close()
        }
    }
}
</script>

<style scoped>
    *{
        user-select: none;
        font-family: 'Courier New', Courier, monospace;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    .node.leaf {
        padding: 10px 0 10px 20px;
        margin-left: 10px;
        background-color: #555f57;
        display: grid;
        grid-template-columns: max-content max-content max-content;
        grid-template-rows: min-content min-content min-content;
        border-radius: 0.5em;
        box-shadow: -3px 3px 8px 1px #272727;
        grid-template-areas: 
            "topl topc topr"
            "midl midc midr"
            "botl botc botr";
    }
    .btnBox {
        grid-area: topr;
        display:flex;
        flex-direction: column;
        width: max-content;
    }
    .getBtn ,
    .watchBtn {
        font-weight: 600;
        font-family: Helvetica,Arial,sans-serif;
        border: None;
        padding: 10px;
        margin: 5px;
        border-radius: 0.5em;
        background: #333333;
        text-transform: uppercase;
        color: #e4e4e4;
    }
    .getBtn {
        align-self: flex-end;
        width: min-content;
    }
    .watchBtn {
        align-self: flex-start;
        width:min-content;
    }
    .getBtn:hover ,
    .watchBtn:hover {
        background: #4e4e4e;
    }
    .getBtn:focus ,
    .watchBtn:focus {
        outline: none;
    }
    .disabled ,
    .disabled:hover{
        background: #e4e4e4;
        color: #646464;
        opacity: 20%;
        
    }
    .watchBtn.on {
        background: #457e55;
    }
    .watchBtn.on:hover {
        background: #5faa74;
    }
    .disp {
        grid-area: topl;
        margin: 10px;
        margin-bottom: 3px;
        margin-top: 3px;
    }
    .value {
        font-style: italic;
        font-weight:bold;
        font-size: 110%;
        color: rgb(255, 255, 255);
    }
    .inp {
        grid-area: botl;
        margin: 10px;
        margin-top: 2px;
    }
</style>top