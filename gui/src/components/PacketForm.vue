<script setup>
import { reactive, ref, computed } from "vue";
import { message } from "ant-design-vue";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";

const props = defineProps({
  onVisualize: Function,
  netns: String,
});

const { getErrorResponse } = useErrorHandling();

const formState = reactive({
  state: "NEW",
  prot: null,
  smac: null,
  dmac: null,
  saddr: null,
  daddr: null,
  sport: null,
  dport: null,
  bridge: null,
  mark: null,
});
const markPacket = ref(false);
const bridgePacket = ref(false);
const ipsetPacket = ref(false);

const portEnable = computed(
  () => formState.prot === "tcp" || formState.prot === "udp"
);

const prots = ref([
  {
    value: null,
    label: "ALL",
  },
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
    value: "NEW",
    label: "NEW",
  },
  {
    value: "ESTABLISHED",
    label: "ESTABLISHED",
  },
  {
    value: "RELATED",
    label: "RELATED",
  },
  {
    value: "INVALID",
    label: "INVALID",
  },
]);

const sending = ref(false);

const onFinish = async () => {
  try {
    sending.value = true;
    props.onVisualize([]);
    const res = await api
      .post(`${API_URL}/${props.netns}/packet`, {
        json: formState,
      })
      .json();
    props.onVisualize(res);
    message.success("Packet sent");
  } catch (error) {
    console.log(error);
    getErrorResponse(error);
  } finally {
    sending.value = false;
  }
};
</script>

<template>
  <div class="packet-form">
    <a-typography-title :level="3">Packet Simulator</a-typography-title>
    <a-space style="margin-bottom: 15px">
      <a-space-compact>
        <a-button :type="bridgePacket ? 'primary' : 'default'" @click="bridgePacket = !bridgePacket">Bridge</a-button>
        <a-button :type="ipsetPacket ? 'primary' : 'default'" @click="ipsetPacket = !ipsetPacket">IPSet</a-button>
        <a-button :type="markPacket ? 'primary' : 'default'" @click="markPacket = !markPacket">Mark</a-button>
      </a-space-compact>
    </a-space>
    <a-form layout="inline" :model="formState" @finish="onFinish">
      <a-form-item>
        <a-select style="width: 120px" placeholder="State" v-model:value="formState.state" :options="states"></a-select>
      </a-form-item>
      <a-form-item>
        <a-select style="width: 120px" placeholder="Protocol" v-model:value="formState.prot" :options="prots"></a-select>
      </a-form-item>
      <a-form-item>
        <a-input v-model:value="formState.smac" placeholder="Source MAC" />
      </a-form-item>
      <a-form-item>
        <a-input v-model:value="formState.dmac" placeholder="Destination MAC" />
      </a-form-item>
      <a-form-item>
        <a-input v-model:value="formState.saddr" placeholder="Source Address" />
      </a-form-item>
      <a-form-item>
        <a-input v-model:value="formState.daddr" placeholder="Destination Address" />
      </a-form-item>
      <a-form-item v-if="portEnable">
        <a-input v-model:value="formState.sport" placeholder="Soure Port" />
      </a-form-item>
      <a-form-item v-if="portEnable">
        <a-input v-model:value="formState.dport" placeholder="Destination Port" />
      </a-form-item>
      <a-form-item v-if="bridgePacket">
        <a-input v-model:value="formState.bridge" placeholder="Bridge" />
      </a-form-item>
      <a-form-item v-if="markPacket">
        <a-input v-model:value="formState.mark" placeholder="Mark" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="sending">Send</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>
