<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";
import IptablesData from "@/components/IptablesData.vue";
import IptablesVisualize from "@/components/IptablesVisualize.vue";
import PacketForm from "@/components/PacketForm.vue";

const route = useRoute();
const router = useRouter();
const { netns } = route.params;
const { getErrorResponse } = useErrorHandling();
const visualizeData = ref();
const interfaces = ref([]);
const ruleset = ref();

const onVisualize = (rules) => {
  visualizeData.value = rules;
};

const getNetns = async () => {
  try {
    const res = await api.get(`${API_URL}/${netns}`).json();
    interfaces.value = res.interfaces;
    ruleset.value = res.ruleset;
  } catch (error) {
    getErrorResponse(error);
    router.push({ name: "NotFoundPage" });
  }
};

const ruleVis = reactive({
  table: null,
  chain: null,
  num: null,
});

const onVisClick = (nodes) => {
  ruleVis.table = null;
  ruleVis.chain = null;

  if (!nodes.length) return;

  const labels = nodes[0].label.split("\n");
  ruleVis.table = labels[0].toLowerCase();
  ruleVis.chain = labels[1];
  ruleVis.num = nodes[0].num;
};

onMounted(async () => {
  await getNetns();
});
await getNetns();
</script>

<template>
  <div class="packet-page">
    <a-space direction="vertical" size="large" style="width: 100%">
      <PacketForm
        :netns="netns"
        :interfaces="interfaces"
        :on-visualize="onVisualize"
      />
      <a-row v-if="visualizeData" :gutter="[16, 8]">
        <a-col :span="16">
          <IptablesVisualize :data="visualizeData" @on-click="onVisClick"
        /></a-col>
        <a-col :span="8">
          <IptablesData :ruleVis="ruleVis" :rules="ruleset"
        /></a-col>
      </a-row>
    </a-space>
  </div>
</template>

<style scoped>
.packet-page {
  margin-top: 30px;
}
</style>
