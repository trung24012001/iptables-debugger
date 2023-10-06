<script setup>
import { toRefs, onMounted, watch } from "vue";
import vis from "vis-network/dist/vis-network.min.js";
import "vis-network/dist/dist/vis-network.min.css";

const props = defineProps({
  data: Array,
});
const emits = defineEmits(["onClick"]);
const { data: dataVisualize } = toRefs(props);

const tables = {
  RAW: {
    color: {
      background: "white",
    },
  },
  MANGLE: {
    color: {
      background: "yellow",
    },
  },
  FILTER: {
    color: {
      background: "orange",
    },
  },
  NAT: {
    color: {
      background: "#0BEC8A",
      // border: "#FFEBD2",
      hover: {
        // background: "#A2CAB8",
        // border: "#0BEC8A",
      },
      highlight: {
        // background: "#CAA2CA",
        // border: "#F009F3",
      },
    },
  },
};

const htmlTitle = (html) => {
  const container = document.createElement("div");
  container.innerHTML = html;
  return container;
};
let level = 0;

const initNetwork = () => {
  const edgesData = dataVisualize.value.map((_, idx) => ({
    from: idx,
    to: idx + 1,
    arrows: "to",
  }));
  const nodesData = dataVisualize.value.map((node, idx) => {
    if (idx % 4 === 3) level += 1;
    return {
      id: idx,
      num: node.num,
      label: `${node.table}\n${node.chain}`,
      title: htmlTitle(
        `<div>${node.rule ? JSON.stringify(node.rule) : node.target}</div>`
      ),
      shape: "box",
      level: level,
      color: tables[node.table].color,
    };
  });

  const nodes = new vis.DataSet(nodesData);
  const edges = new vis.DataSet(edgesData);
  const container = document.getElementById("mynetwork");
  const data = {
    nodes: nodes,
    edges: edges,
  };
  const options = {
    autoResize: true,
    width: "100%",
    height: "600px",
    nodes: {
      margin: 12,
      font: {
        multi: "html",
        color: "#000",
        size: 16,
      },
    },
    edges: {
      smooth: false,
      length: 200,
    },
    layout: {
      hierarchical: true,
    },
    interaction: {
      hover: true,
      hoverConnectedEdges: false,
    },
  };
  const network = new vis.Network(container, data, options);

  network.on("click", (properties) => {
    const ids = properties.nodes;
    emits("onClick", nodes.get(ids));
  });
};

onMounted(() => {
  initNetwork();
});

watch(dataVisualize, () => {
  initNetwork();
});
</script>

<template>
  <div id="mynetwork"></div>
</template>

<style scoped>
#mynetwork {
  border: 1px solid #000;
}
</style>
