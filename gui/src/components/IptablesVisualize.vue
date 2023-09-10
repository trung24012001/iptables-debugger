<script setup>
import { toRefs } from "vue";
const props = defineProps({
  data: Array,
});
const { data } = toRefs(props);

console.log(data.value[0]);
</script>

<template>
  {{ data }}
</template>

<style scoped></style>
