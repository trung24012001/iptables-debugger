<script setup>
import { toRefs, onMounted, computed, watch } from "vue";
import vis from "vis-network/dist/vis-network.min.js";
import "vis-network/dist/dist/vis-network.min.css";

const props = defineProps({
  data: Array,
});
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
  const edgesData = dataVisualize.value.map((_, idx) => ({ from: idx, to: idx + 1, arrows: "to" }));
  const nodesData = dataVisualize.value.reduce((acc, curVal, idx) => {
    if (idx % 4 === 3) level += 1;
    acc.push({
      id: idx,
      label: `${curVal.table}\n${curVal.chain}`,
      title: htmlTitle(`<div>${curVal.rule ? JSON.stringify(curVal.rule) : curVal.target}</div>`),
      shape: "box",
      level: level,
      color: tables[curVal.table].color,
    });
    return acc;
  }, []);

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
  network.moveTo({
    position: { x: 0, y: 0 },
    offset: { x: -600 / 2, y: -600 / 2 },
    scale: 1,
  });
}

onMounted(() => {
  initNetwork()
});

watch(dataVisualize, () => {
  initNetwork()
})

</script>

<template>
  <div id="mynetwork"></div>
</template>

<style scoped>
#mynetwork {
  border: 1px solid #000;
}
</style>
