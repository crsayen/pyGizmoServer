<template>
    <div class="node">
        <div>{{ label }}</div>
        <LeafNode
            v-for="node in leafnodes"
            :label="node.label"
            :type="node.type"
            :writable="node.writable"
            :readable="node.readable"
            :path="node.path"
            :key="node.id"
        ></LeafNode>
        <BranchNode 
            v-for="node in branchnodes" 
            :nodes="node.nodes" 
            :label="node.label"
            :key="node.id"
        >
        </BranchNode>
    </div>
</template>


<script>
import LeafNode from './LeafNode.vue'

export default { 
    name: 'BranchNode',
    props: [ 'label', 'nodes'],
    components : {
        LeafNode
    },
    computed: {
        leafnodes() {
            return this.nodes.map(node => node.isleaf)
        },
        branchnodes() {
            return this.nodes.map(node => !node.isleaf)
        }
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
</style>