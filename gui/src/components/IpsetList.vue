<script setup>
import { toRefs } from "vue";

const props = defineProps({
  netns: String
})
const { netns } = toRefs(props)

</script>

<template>
  <div class="ipset-list">
    <a-typography-title :level="3">IPSet</a-typography-title>
    <div>
      Run this script curl -s http://10.100.10.182:8000/api/{{ netns }}/ipset | bash
    </div>
  </div>
</template>
