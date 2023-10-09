<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { message } from "ant-design-vue";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";
import { UploadOutlined } from "@ant-design/icons-vue";

const { getErrorResponse } = useErrorHandling();
const router = useRouter();
const fileList = ref([]);
const uploading = ref(false);
const rules = ref();
const netns = ref();

const handleUpload = async () => {
  const formData = new FormData();
  formData.append("rules", rules.value);
  uploading.value = true;
  try {
    const res = await api
      .post(`${API_URL}/iptables`, {
        body: formData,
      })
      .text();
    netns.value = res;
    message.success("Upload successfully");
  } catch (error) {
    console.log(error)
    getErrorResponse(error);
  } finally {
    uploading.value = false;
    fileList.value = [];
    rules.value = null;
  }
};

const beforeUpload = (file) => {
  if (file.size > 1024 * 1024) {
    message.error("File maximum 1MB")
    return false
  }
  const reader = new FileReader()
  reader.onload = e => rules.value = e.target.result;
  reader.readAsText(file);
  return false;
};

</script>

<template>
  <div class="iptables-page">
    <a-space direction="vertical" style="width: 800px;">
      <div>
        Run this script for quickly setting up curl -s http://10.100.10.182:8000/api/setup | bash
      </div>
      <a-typography-title :level="3">Upload IPTables Ruleset</a-typography-title>
      <a-upload :before-upload="beforeUpload" :max-count="1" v-model:file-list="fileList">
        <a-button>
          <upload-outlined />
          Upload
        </a-button>
      </a-upload>
      <a-textarea v-model:value="rules" placeholder="IPTables rules" :rows="8" />
      <a-space style="margin-top: 15px">
        <a-button type="primary" :disabled="!rules" :loading="uploading" @click="handleUpload">Submit</a-button>
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
