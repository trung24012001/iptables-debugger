<script setup>
</script>

<template>
  <div class="app">
    <a-typography-title>IPTables Debugger</a-typography-title>
    <router-view v-slot="{ Component }">
      <Suspense timeout="0">
        <component :is="Component" />
        <template #fallback>
          <div class="loading">
            <a-spin />
          </div>
        </template>
      </Suspense>
    </router-view>
  </div>
</template>

<style scoped>
.app {
  margin: 30px 60px;
}
</style>
