<script setup>
import { ref } from "vue"
import IptablesData from "@/components/IptablesData.vue";
import IptablesTable from "@/components/IptablesTable.vue";
import IptablesVisualize from "@/components/IptablesVisualize.vue";
import PacketForm from "@/components/PacketForm.vue";


const ipset = ref(false);

const onUploadRuleset = async () => {
  console.log("upload")
}

const onUploadIpset = async () => {
  console.log("ipset upload")
}

</script>

<template>
  <div class="iptables-page">
    <a-button
      :type="ipset ? 'primary' : 'default'"
      @click="ipset = !ipset"
      >IPSet</a-button
    >
    <a-typography-title :level="3">Upload IPTables Ruleset</a-typography-title>

    <a-button
     type="primary"
     @click="onUploadRuleset"
     >Upload</a-button>
    
    <a-space v-if="ipset">
      <a-typography-title :level="3">Upload IPSet</a-typography-title>
      <a-button
       type="primary"
       @click="onUploadIpset"
       >Upload</a-button>
    </a-space>
  </div>
</template>

<style scoped>
.iptables-page {
  margin: 30px 60px;
}
</style>
