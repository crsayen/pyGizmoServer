<template>
    <div class="leaf node">
        <div class="labelBox">
            {{ label }}
        </div>
        <div class="valueBox">
            <div class='valueLabel'>state:</div>
            <div class="value">{{ value }}</div>
        </div>
        <div v-if="writable" class="input">
            <b-form-checkbox switch size="lg" v-if="type == 'boolean'" v-model="outValue">
            </b-form-checkbox>
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
                    v-text="watching ? 'watching' : 'watch'"
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
                    value: (isNaN(value)) ? value : Number(value)
                })
            })
            .then((response) => response.json())
            .then((res) => {
                if (!this.watching) {
                    console.log(res)
                    this.value = res[0].data
                }
            }
        )},
        watch_unwatch() {
            if (!this.watching) {
                this.ws = new ws('ws://localhost:11111' + this.path)
                this.ws.onmessage = (data) => {
                    console.log(data)
                    this.value = JSON.parse(data.data).value
                }
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
                console.log(newVal)
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

