<template>
    <div class="node">
        <div class="lbl">{{ label }}</div>
        <leafnode
            v-for="node in leafnodes"
            :label="node.label"
            :type="node.type"
            :writable="node.writable"
            :readable="node.readable"
            :path="node.path"
            :key="node.id"
        ></leafnode>
        <branchnode 
            v-for="node in branchnodes" 
            :nodes="node.nodes" 
            :label="node.label"
            :key="node.id"
        >
        </branchnode>
    </div>
</template>


<script>
import leafnode from './leafnode.vue'

export default { 
    props: [ 'label', 'nodes'],
    name: 'branchnode',
    components : {
        leafnode,
    },
    computed: {
        leafnodes() {
            return this.nodes.filter(node => node.isleaf)
        },
        branchnodes() {
            return this.nodes.filter(node => !node.isleaf)
        }
    }
}
</script>

<style scoped>
    .node{
        padding: 10px;
        letter-spacing: 1px;
        font-family: 'Courier New', Courier, monospace;
        margin: 10px;
        margin-left: 1px;
        box-shadow: -3px 3px 8px 1px #181818;
        background-color: rgb(59, 59, 59);
        color:rgb(224, 224, 224);
        font-weight: bold;
        min-width: max-content;
    }
    .lbl {
        margin-left: 20px;
    }
</style>