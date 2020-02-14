<template>
    <div class="main" id="app">        
        <div id="ui">
            <div id="buttonbar"></div>
        </div>
        <div id="treecontainer"></div>
    </div>
</template>

<script>
import Vue from 'vue'
import DynamicComponent from './components/DynamicComponent'

	export default {
    name: 'app',
    components: { DynamicComponent },
    methods: {
      load() {
          fetch("/model")
            .then(async (response) => {
                model = await response.json();
                console.log(model);
                Object.keys(model.data).forEach((root, index, array) => {
                    var ComponentClass = Vue.extend(Button)
                    var instance = new ComponentClass({
                        propsData: { type: 'primary' }
                    })
                    instance.$slots.default = ['root']
                    instance.$mount() // pass nothing
                    // TODO: add the showtree() method to each button, utilizing DynamicComponent to watch values in real time
                    this.$refs.buttonbar.appendChild(instance.$el)
                });
            }
        );
      }
    }
  }
</script>
