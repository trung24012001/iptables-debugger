<script setup>
import { reactive, ref, computed } from "vue";
const formState = reactive({
  saddr: null,
  sport: null,
  daddr: null,
  dport: null,
  protocol: null,
  state: null,
  bridgePort: null,
  mark: null,
});
const statePacket = ref(false);
const ipsetPacket = ref(false);
const markPacket = ref(false);
const bridgePacket = ref(false);

const portEnable = computed(
  () => formState.protocol === "tcp" || formState.protocol === "udp"
);

const protocols = ref([
  {
    value: "tcp",
    label: "TCP",
  },
  {
    value: "udp",
    label: "UDP",
  },
  {
    value: "icmp",
    label: "ICMP",
  },
]);

const states = ref([
  {
    value: "new",
    label: "NEW",
  },
  {
    value: "established",
    label: "ESTABLISHED",
  },
  {
    value: "related",
    label: "RELATED",
  },
]);

const onFinish = (values) => {
  console.log("Success:", values);
};
</script>

<template>
  <div class="packet-form">
    <a-typography-title :level="3">Packet Simulator</a-typography-title>
    <a-space :size="0" style="margin-bottom: 15px">
      <a-button
        :type="statePacket ? 'primary' : 'default'"
        @click="statePacket = !statePacket"
        >State</a-button
      >
      <a-button
        :type="ipsetPacket ? 'primary' : 'default'"
        @click="ipsetPacket = !ipsetPacket"
        >IPSet</a-button
      >
      <a-button
        :type="bridgePacket ? 'primary' : 'default'"
        @click="bridgePacket = !bridgePacket"
        >Bridge</a-button
      >
      <a-button
        :type="markPacket ? 'primary' : 'default'"
        @click="markPacket = !markPacket"
        >Mark</a-button
      >
    </a-space>
    <a-form layout="inline" :model="formState" @finish="onFinish">
      <a-form-item>
        <a-select
          style="width: 120px"
          placeholder="Protocol"
          v-model:value="formState.protocol"
          :options="protocols"
        ></a-select>
      </a-form-item>
      <a-form-item>
        <a-input v-model:value="formState.saddr" placeholder="Source Address" />
      </a-form-item>
      <a-form-item v-if="portEnable">
        <a-input v-model:value="formState.sport" placeholder="Soure Port" />
      </a-form-item>
      <a-form-item>
        <a-input
          v-model:value="formState.daddr"
          placeholder="Destination Address"
        />
      </a-form-item>
      <a-form-item v-if="portEnable">
        <a-input
          v-model:value="formState.dport"
          placeholder="Destination Port"
        />
      </a-form-item>
      <a-form-item v-if="statePacket">
        <a-select
          style="width: 120px"
          placeholder="State"
          v-model:value="formState.state"
          :options="states"
        ></a-select>
      </a-form-item>
      <a-form-item v-if="bridgePacket">
        <a-input
          v-model:value="formState.bridgePort"
          placeholder="Bridge Port"
        />
      </a-form-item>
      <a-form-item v-if="markPacket">
        <a-input v-model:value="formState.mark" placeholder="Mark" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit">Send</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>
