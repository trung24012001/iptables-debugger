<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";
import IptablesData from "@/components/IptablesData.vue";
import IptablesTable from "@/components/IptablesTable.vue";
import IptablesVisualize from "@/components/IptablesVisualize.vue";
import PacketForm from "@/components/PacketForm.vue";

const route = useRoute();
const router = useRouter();
const { netns } = route.params;
const { getErrorResponse } = useErrorHandling();
const visualizeData = ref();

const onVisualize = (rules) => {
  visualizeData.value = rules;
};

const checkNetns = async () => {
  try {
    await api.get(`${API_URL}/${netns}`);
  } catch (error) {
    getErrorResponse(error);
    router.push({ name: "NotFoundPage" });
  }
};
checkNetns();
</script>

<template>
  <div class="packet-page">
    <a-space direction="vertical" size="large">
      <PacketForm :netns="netns" :on-visualize="onVisualize" />
      <IptablesData />
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
