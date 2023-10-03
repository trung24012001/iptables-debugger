<script setup>
import { toRefs, computed } from 'vue';


const props = defineProps({
  data: Array,
});

const { data: dataVisualize } = toRefs(props)

const dataSource = computed(() => dataVisualize.value.map((item, idx) => {
  return {
    key: idx,
    num: item.num,
    counters: item.rule?.counters,
    table: item.table,
    chain: item.chain,
    protocol: item.rule?.protocol,
    src: item.rule?.src,
    dst: item.rule?.dst,
    target: item.target,
  };
}));

const columns = [
  {
    title: "Rule Number",
    dataIndex: "num",
    key: "num",
  },
  {
    title: "Counters",
    dataIndex: "counters",
    key: "counters",
  },
  {
    title: "Table",
    dataIndex: "table",
    key: "table",
  },
  {
    title: "Chain",
    dataIndex: "chain",
    key: "chain",
  },
  {
    title: "Protocol",
    dataIndex: "protocol",
    key: "protocol",
  },
  {
    title: "Source",
    dataIndex: "src",
    key: "src",
  },
  {
    title: "Destination",
    dataIndex: "dst",
    key: "dst",
  },
  {
    title: "Target",
    dataIndex: "target",
    key: "target",
  },
];

const handleResizeColumn = (w, col) => {
  col.width = w;
};
</script>

<template>
  <a-table :dataSource="dataSource" :columns="columns" :pagination="false" @resizeColumn="handleResizeColumn">
    <template #bodyCell="{ column, text, record }">
      <template v-if="column.dataIndex === 'target'">
        {{ text }}
      </template>
      <template v-else-if="['src', 'dst'].includes(column.dataIndex)">
        {{ text ? text : (record.num ? "0.0.0.0/0" : "") }}
      </template>
      <template v-else>
        {{ text ? text : (record.num ? "*" : "") }}
      </template>
    </template>
  </a-table>
</template>
