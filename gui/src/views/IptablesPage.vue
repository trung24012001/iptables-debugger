<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { message } from "ant-design-vue";
import { UploadOutlined } from '@ant-design/icons-vue';
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";


const router = useRouter()
const { getErrorResponse } = useErrorHandling();
const fileUpload = ref();
const uploading = ref(false)
const netns = ref();


const beforeUpload = (file) => {
  fileUpload.value = file;
  return false;
}

const handleUploadRuleset = async () => {
  const formData = new FormData();
  formData.append("filedata", fileUpload.value);
  uploading.value = true;
  try {
    const res = await api.post(`${API_URL}/iptables`, {
      body: formData,              
    }).json();
    netns.value = res.netns;
    message.success("Upload successfully")
  } catch(error) {
    getErrorResponse(error);
  } finally {
    fileUpload.value = undefined;
    uploading.value = false;
  } 
}

</script>

<template>
  <div class="iptables-page">
    <a-space direction="vertical">
      <a-typography-title :level="3">Upload IPTables Ruleset</a-typography-title>
      <a-upload
        :before-upload="beforeUpload"
        :max-count="1"
       >
        <a-button>
          <upload-outlined />
          Upload
        </a-button>
      </a-upload>
    <a-button
     type="primary"
     :disabled="!fileUpload"
     :loading="uploading"
     @click="handleUploadRuleset"
     >Submit</a-button>
    <a-button
     type="primary"
     @click="() => router.push(netns)"
     v-if="netns"
     >Simulate</a-button>
    </a-space>
  </div>
</template>

<style scoped>
.iptables-page {
  margin: 30px 60px;
}
</style>
