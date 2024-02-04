<script setup>
import { toRefs } from "vue";

const props = defineProps({
  interfaces: Array,
  netns: String,
});

const { interfaces, netns } = toRefs(props);
</script>

<template>
  <div class="iface-list">
    <a-typography-title :level="3">Interfaces</a-typography-title>
    <div>
      Run this script curl -s http://10.100.10.182:8000/api/{{
        netns
      }}/interfaces | bash
    </div>
    <a-space direction="vertical" style="width: 100%">
      <div class="group-input" v-for="(item, idx) in interfaces" :key="idx">
        <a-input-group compact style="width: 80%" disabled>
          <a-input
            style="width: 15%"
            v-model:value="item.ifname"
            :disabled="true"
            placeholder="type"
          />
          <a-input
            style="width: 15%"
            v-model:value="item.type"
            :disabled="true"
          />
          <a-input
            style="width: 30%"
            v-model:value="item.addr"
            :disabled="true"
          />
          <a-input
            style="width: 30%"
            v-model:value="item.mac"
            :disabled="true"
            placeholder="mac"
          />
        </a-input-group>
      </div>
    </a-space>
  </div>
</template>

<style scoped>
.group-input {
  display: flex;
}
</style>
