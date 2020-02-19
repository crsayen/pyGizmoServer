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
        <b-button v-b-toggle='this.path' variant="primary">Toggle Collapse</b-button>
        <b-collapse id="this.path" class="mt-2">
        <branchnode 
            v-for="node in branchnodes" 
            :nodes="node.nodes" 
            :label="node.label"
            :key="node.id"
        >
        </branchnode>
        </b-collapse>
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
