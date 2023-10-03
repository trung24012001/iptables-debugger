<script setup>
import { defineEmits, defineProps, toRefs, ref, watch } from "vue";
import { UploadOutlined } from "@ant-design/icons-vue";

const emits = defineEmits(["onUpload"]);
const props = defineProps({
  fileUpload: Object,
});

const { fileUpload } = toRefs(props);
const fileList = ref([]);

const beforeUpload = (file) => {
  emits("onUpload", file);
  return false;
};

watch(fileUpload, (newVal, _) => {
  if (!newVal) fileList.value = [];
});
</script>

<template>
  <div class="iptables-upload">
    <a-typography-title :level="3">Upload IPTables Ruleset</a-typography-title>
    <a-upload
      :before-upload="beforeUpload"
      :max-count="1"
      v-model:file-list="fileList"
    >
      <a-button>
        <upload-outlined />
        Upload
      </a-button>
    </a-upload>
  </div>
</template>
