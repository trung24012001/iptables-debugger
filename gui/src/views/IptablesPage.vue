<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { message } from "ant-design-vue";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";
import EtherInput from "@/components/EtherInput.vue";
import IptablesUpload from "@/components/IptablesUpload.vue";

const router = useRouter();
const { getErrorResponse } = useErrorHandling();
const netns = ref();
const interfaces = ref();
const fileUpload = ref();
const uploading = ref(false);

const onUpload = (file) => {
  fileUpload.value = file;
};

const handleUpload = async () => {
  const formData = new FormData();
  formData.append("filedata", fileUpload.value);
  formData.append("interfaces", JSON.stringify(interfaces.value));
  uploading.value = true;
  try {
    const res = await api
      .post(`${API_URL}/iptables`, {
        body: formData,
      })
      .json();
    netns.value = res.netns;
    message.success("Upload successfully");
  } catch (error) {
    getErrorResponse(error);
  } finally {
    fileUpload.value = undefined;
    uploading.value = false;
  }
};

const onEtherChange = (ethers) => {
  interfaces.value = ethers;
};
</script>

<template>
  <div class="iptables-page">
    <a-space size="large" direction="vertical" style="width: 1000px">
      <iptables-upload @on-upload="onUpload" :fileUpload="fileUpload" />
      <ether-input @on-change="onEtherChange" />
      <a-space style="margin-top: 25px">
        <a-button type="primary" :disabled="!fileUpload" :loading="uploading" @click="handleUpload">Submit</a-button>
        <a-button type="primary" @click="() => router.push(netns)" v-if="netns">Simulate</a-button>
      </a-space>
    </a-space>
  </div>
</template>

<style scoped>
.iptables-page {
  margin: 30px 60px;
}
</style>
