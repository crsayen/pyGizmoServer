<template>
    <div class="node">
        <div class="label">{{ label }}</div>
        <b-button
            size='sm'
            block
            class="expander"
            :pressed.sync="expanded"
            v-if="!this.isroot && this.nodes.length > 1"
            v-b-toggle="'collapse-' + this.label" 
            v-text="(expanded) ? '-' : '+'"
        ></b-button>
        <b-collapse
            :visible="this.isroot || (!this.root && this.nodes.length < 2)"
            :id="'collapse-' + this.label"
            class="mt-2"
        >
            <branchnode 
                v-for="node in branchnodes" 
                :nodes="node.nodes" 
                :label="node.label"
                :key="node.id"
            >
            </branchnode>
            <leafnode
                v-for="node in leafnodes"
                :label="node.label"
                :type="node.type"
                :writable="node.writable"
                :readable="node.readable"
                :path="node.path"
                :key="node.id"
            ></leafnode>
        </b-collapse>
    </div>
</template>


<script>
import leafnode from './leafnode.vue'

export default { 
    props: [ 'label', 'nodes', 'isroot'],
    name: 'branchnode',
    data() {return {expanded: false}},
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
