<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";
import IptablesTable from "@/components/IptablesTable.vue";
import IptablesVisualize from "@/components/IptablesVisualize.vue";
import PacketForm from "@/components/PacketForm.vue";

const route = useRoute();
const router = useRouter();
const { netns } = route.params;
const { getErrorResponse } = useErrorHandling();
const visualizeData = ref();
const interfaces = ref([]);

const onVisualize = (rules) => {
  visualizeData.value = rules;
};

const getNetns = async () => {
  try {
    const res = await api.get(`${API_URL}/${netns}`).json();
    interfaces.value = res;
  } catch (error) {
    getErrorResponse(error);
    router.push({ name: "NotFoundPage" });
  }
};

onMounted(async () => {
  await getNetns();
})
await getNetns();
</script>

<template>
  <div class="packet-page">
    <a-space direction="vertical" size="large">
      <PacketForm :netns="netns" :interfaces="interfaces" :on-visualize="onVisualize" />
      <div v-if="visualizeData">
        <IptablesVisualize :data="visualizeData" />
        <IptablesTable :data="visualizeData" />
      </div>
    </a-space>
  </div>
</template>

<style scoped>
.packet-page {
  margin: 30px 60px;
}
</style>
