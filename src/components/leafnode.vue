<template>
    <div class="leaf node">
        <div class="labelBox">
            {{ label }}
        </div>
        <div class="valueBox">
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
                >get</button>
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
    props: [ 'label', 'type', "writable", "readable", "path", "wsurl"],
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
                console.log(json)
                if (!this.watching){
                    this.value = (json[0]) ? json[0].data : json.data
                }
            })
        },
        patch(body) {
            fetch(this.path, { headers: {
                    "Content-Type": "application/json; charset=utf-8"
                },
                method: 'PATCH',
                body: body
            })
            .then((response) => response.json())
            .then((res) => {
                if (res[0].error){
                    alert(res[0].error)
                }
                if (!this.watching) {
                    this.value = res[0].data
                }
            }
        )},
        watch_unwatch() {
            if (!this.watching) {
                this.get()
                this.ws = new ws(this.wsurl + ':11111' + this.path)
                this.ws.onmessage = (data) => {
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
            let body
            if (newVal != oldVal){
                body = JSON.stringify({
                    op: 'replace',
                    path: this.path,
                    value: (["string", "hex", "integer"].includes(this.type)) ?
                        ((this.type == "integer") ? Number(newVal) : String(newVal)) : newVal
                })
                this.patch(body)
            }
        }
    },
    mounted() {
        if (this.readable){this.get()}
    },
    destroyed() {
        if (this.ws !== null){
            this.ws.close()
        }
    }
}
</script>

