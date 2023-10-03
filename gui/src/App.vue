<script setup>
</script>

<template>
  <div class="app">
    <a-typography-title>IPTables Debugger</a-typography-title>
    <Suspense>
      <template #default>
        <router-view />
      </template>
      <template #fallback>
        <a-spin />
      </template>
    </Suspense>
  </div>
</template>

<style scoped>
.app {
  margin: 30px 60px;
}
</style>
