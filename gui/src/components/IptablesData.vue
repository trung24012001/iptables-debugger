<script setup>
import { toRefs, computed, ref, reactive, watch } from "vue";

const props = defineProps({
  ruleVis: Object,
  rules: String,
});

const { rules, ruleVis } = toRefs(props);

const collapsedTables = reactive({
  security: true,
  raw: true,
  mangle: true,
  filter: true,
  nat: true,
});

const formatedRules = computed(() => formatRules());

const formatRules = () => {
  let isCollapse = false;
  let isHighlight = false;
  let ruleNum = 0;

  return rules.value.split("\n").map((row, idx) => {
    // Get rule number
    if (row.includes(`-A ${ruleVis.value.chain} `)) ruleNum++;
    else ruleNum = 0;

    // Highlight
    let newRow = row;
    if (row.includes(`*${ruleVis.value.table}`)) isHighlight = true;

    if (isHighlight) {
      newRow = `<div class="table-active">${row}</div>`;
      if (ruleVis.value.num && ruleVis.value.num === ruleNum) {
        console.log(ruleVis.value.num, ruleNum);
        newRow = `<div class="table-active rule-active">${row}</div>`;
      }
      if (
        ruleVis.value.num === null &&
        row.includes(`:${ruleVis.value.chain} `)
      )
        newRow = `<div class="table-active rule-active">${row}</div>`;
    }

    if (row.search(/^COMMIT$/) >= 0) isHighlight = false;

    // Collapse
    let table = getTable(row);
    if (table) isCollapse = collapsedTables[table];

    return {
      id: idx + 1,
      html: newRow,
      collapse: isCollapse,
    };
  });
};

const getTable = (text) => {
  const found = text.match(/\*\w+/);
  if (!found) return "";
  return found[0].split("*")[1];
};

const handleCollapse = (item) => {
  let table = getTable(item.html);
  if (!table) return;
  collapsedTables[table] = !collapsedTables[table];
};

watch(
  ruleVis,
  (newRule, _) => {
    if (!newRule.table) return;
    for (let k in collapsedTables) collapsedTables[k] = true;
    collapsedTables[newRule.table] = false;
  },
  {
    deep: true,
  }
);
</script>

<template>
  <div class="iptables-table">
    <template v-for="row in formatedRules" :key="row.id">
      <a-row :gutter="[8, 8]" v-if="getTable(row.html) || !row.collapse">
        <a-col :span="3" class="number-editor">
          {{ row.id }}
          <span
            :class="{
              'ace-editor': true,
              'ace-editor-open': !row.collapse,
              'ace-editor-close': row.collapse,
            }"
            @click="handleCollapse(row)"
            v-if="getTable(row.html)"
          ></span>
        </a-col>
        <a-col :span="21" v-html="row.html" class="row-editor"></a-col>
      </a-row>
    </template>
  </div>
</template>
<style>
.iptables-table {
  display: block;
  height: 600px;
  overflow: scroll;
}
.table-active {
  color: blue;
  background-color: #eee;
}

.rule-active {
  font-weight: 700;
  padding-left: 3px;
}

.number-editor {
  background-color: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
}

.row-editor {
  line-height: 1.8;
}

.ace-editor {
  display: inline-block;
  position: absolute;
  right: 5%;
  width: 11px;
  height: 80%;
  cursor: pointer;
  background-repeat: no-repeat;
  background-position: center;
}

.ace-editor:hover {
  border: 1px solid #9f9f9f;
  border-radius: 3px;
}

.ace-editor:active {
  opacity: 0.6;
}

.ace-editor-open {
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAANElEQVR42mWKsQ0AMAzC8ixLlrzQjzmBiEjp0A6WwBCSPgKAXoLkqSot7nN3yMwR7pZ32NzpKkVoDBUxKAAAAABJRU5ErkJggg==");
}

.ace-editor-close {
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAAGCAYAAAAG5SQMAAAAOUlEQVR42jXKwQkAMAgDwKwqKD4EwQ26sSOkVWjgIIHAzPiCgaqiqnJHZnKICBERHN194O5b9vbLuAVRL+l0YWnZAAAAAElFTkSuQmCCXA==");
}
</style>
