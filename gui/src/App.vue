<script setup>
// import HelloWorld from "@/components/HelloWorld.vue";
import IptablesVisualize from "./components/IptablesVisualize.vue";

const data = [
  {
    state: null,
    num: 1,
    rule: {
      protocol: "tcp",
      target: { DNAT: { "to-destination": "10.10.1.150:22" } },
      tcp: { dport: "15022" },
      counters: "(27L, 1096L)",
    },
    chain: "PREROUTING",
    target: { DNAT: { "to-destination": "10.10.1.150:22" } },
  },
  {
    state: null,
    num: 1,
    rule: {
      target: "neutron-filter-top",
      counters: "(1406825176L, 1353047544246L)",
    },
    chain: "FORWARD",
    target: "neutron-filter-top",
  },
  {
    state: null,
    num: 1,
    rule: {
      target: "neutron-linuxbri-local",
      counters: "(2804605847L, 8006988838507L)",
    },
    chain: "neutron-filter-top",
    target: "neutron-linuxbri-local",
  },
  {
    state: null,
    num: null,
    rule: null,
    chain: "neutron-linuxbri-local",
    target: "",
  },
  {
    state: null,
    num: null,
    rule: null,
    chain: "neutron-filter-top",
    target: "",
  },
  {
    state: null,
    num: 2,
    rule: {
      target: "neutron-linuxbri-FORWARD",
      counters: "(1406825176L, 1353047544246L)",
    },
    chain: "FORWARD",
    target: "neutron-linuxbri-FORWARD",
  },
  {
    state: null,
    num: null,
    rule: null,
    chain: "neutron-linuxbri-FORWARD",
    target: "",
  },
  { state: null, num: null, rule: null, chain: "FORWARD", target: "ACCEPT" },
  {
    state: null,
    num: 3,
    rule: {
      src: "192.168.122.0/24",
      dst: "!192.168.122.0/24",
      protocol: "tcp",
      target: { MASQUERADE: { "to-ports": "1024-65535" } },
      counters: "(0L, 0L)",
    },
    chain: "POSTROUTING",
    target: { MASQUERADE: { "to-ports": "1024-65535" } },
  },
];
</script>

<template>
  <IptablesVisualize :data="data" />
  <!-- <div>
    <a href="https://vitejs.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
  </div>
  <HelloWorld msg="Vite + Vue" /> -->
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
