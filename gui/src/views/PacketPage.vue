<script setup>
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api"
import IptablesData from "@/components/IptablesData.vue";
import IptablesTable from "@/components/IptablesTable.vue";
import IptablesVisualize from "@/components/IptablesVisualize.vue";
import PacketForm from "@/components/PacketForm.vue";


const data = [
  {
    table: "nat",
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
    table: "filter",
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
    table: "filter",
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
    table: "filter",
    state: null,
    num: null,
    rule: null,
    chain: "neutron-linuxbri-local",
    target: "",
  },
  {
    table: "filter",
    state: null,
    num: null,
    rule: null,
    chain: "neutron-filter-top",
    target: "",
  },
  {
    table: "filter",
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
    table: "filter",
    state: null,
    num: null,
    rule: null,
    chain: "neutron-linuxbri-FORWARD",
    target: "",
  },
  {
    table: "filter",
    state: null,
    num: null,
    rule: null,
    chain: "FORWARD",
    target: "ACCEPT",
  },
  {
    table: "nat",
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
const API_URL = import.meta.env.VITE_API_URL;
const route = useRoute();
const router = useRouter();
const { netns } = route.params;

const checkNs = async () => {
  try {
    await api.get(`${API_URL}/${netns}`).json();
  } catch {
    router.push({ name: "NotFoundPage" })
  }
}
checkNs()


</script>

<template>
  <div class="packet-page">
    <a-space direction="vertical" size="large">
      <PacketForm />
      <IptablesData />
      <IptablesVisualize :data="data" />
      <IptablesTable :data="data" />
    </a-space>
  </div>
</template>

<style scoped>
.packet-page {
  margin: 30px 60px;
}
</style>
