<script setup>
import { h, reactive, ref, watch, defineEmits } from "vue";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons-vue";

const emit = defineEmits(["onChange"]);

const inputs = reactive([
  {
    id: new Date(),
    link: "loopback",
    type: "dummy",
    name: "lo",
    addr: "127.0.0.1",
    mac: "00:00:00:00:00:00",
    disabled: true,
  },
]);

// const types = ref([
//   {
//     value: "dummy",
//     label: "default",
//   },
//   {
//     value: "bridge",
//     label: "bridge",
//   },
// ]);

const handleAdd = () => {
  inputs.push({ id: new Date(), link: "ether", type: "dummy", name: "ethname" });
};

const handleDelete = (id) => {
  const pos = inputs.findIndex((item) => item.id === id);
  inputs.splice(pos, 1);
};

watch(
  inputs,
  (newInputs, _) => {
    emit("onChange", newInputs.slice(1));
  },
  { immediate: true }
);
</script>

<template>
  <div class="ether-input">
    <a-typography-title :level="3">Interfaces</a-typography-title>
    <a-space direction="vertical" style="width: 100%">
      <div class="group-input" v-for="(item, idx) in inputs" :key="item.id">
        <a-input-group compact style="width: 80%" disabled>
          <a-button style="width: 10%" :disabled="item.disabled">{{
            item.link
          }}</a-button>
          <!-- <a-select style="width: 15%" v-model:value="item.type" :options="types" :disabled="item.disabled" /> -->
          <a-input style="width: 15%" v-model:value="item.name" :disabled="item.disabled" placeholder="ifname" />
          <a-input style="width: 30%" v-model:value="item.addr" :disabled="item.disabled" placeholder="addr" />
          <a-input style="width: 30%" v-model:value="item.mac" :disabled="item.disabled" placeholder="mac" />
        </a-input-group>
        <a-space>
          <a-button shape="circle" :icon="h(DeleteOutlined)" style="margin: 0px 5px" @click="handleDelete(item.id)" danger
            v-if="!item.disabled" />
          <a-button shape="circle" :icon="h(PlusOutlined)" @click="handleAdd" v-if="idx === inputs.length - 1" />
        </a-space>
      </div>
    </a-space>
  </div>
</template>

<style scoped>
.group-input {
  display: flex;
}
</style>
