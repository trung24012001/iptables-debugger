<script setup>
import { toRefs, onMounted } from "vue";
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
      // border: "#FFEBD2",
      background: "#0BEC8A",
      hover: {
        background: "#A2CAB8",
        // border: "#0BEC8A",
      },
      highlight: {
        // border: "#F009F3",
        background: "#CAA2CA",
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
const edgesData = [];
const nodesData = dataVisualize.value.reduce((acc, curVal, idx) => {
  edgesData.push({ from: idx, to: idx + 1, arrows: "to" });
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

onMounted(() => {
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
      margin: 10,
      font: {
        multi: "html",
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
  // network.moveTo({
  //   position: { x: 0, y: 0 },
  //   offset: { x: -width / 2, y: -height / 2 },
  //   scale: 1,
  // });
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
