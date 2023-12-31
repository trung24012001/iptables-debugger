<script setup>
import { reactive, ref, computed, toRefs } from "vue";
import { message } from "ant-design-vue";
import { api, API_URL } from "@/services/api";
import { useErrorHandling } from "@/services/errorHandling";

const props = defineProps({
  onVisualize: Function,
  netns: String,
  interfaces: Array,
});

const { onVisualize, netns, interfaces } = toRefs(props);

const { getErrorResponse } = useErrorHandling();

const formState = reactive({
  state: "NEW",
  prot: "icmp",
  smac: null,
  dmac: null,
  ininf: null,
  outinf: null,
  saddr: null,
  daddr: null,
  sport: null,
  dport: null,
  mark: null,
});

const btnState = reactive({
  flow: false,
  mac: false,
  mark: false,
});

const flowState = ref();
const ifaceState = ref();

const prots = ref([
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

const flows = ref([
  { value: "in", label: "IN" },
  { value: "out", label: "OUT" },
]);

const ethers = computed(() =>
  interfaces.value.map((item) => ({
    value: item.ifname,
    label: item.ifname,
  }))
);

const portEnable = computed(
  () => formState.prot === "tcp" || formState.prot === "udp"
);

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
    onVisualize.value([]);
    const res = await api
      .post(`${API_URL}/${netns.value}/packet`, {
        json: formState,
      })
      .json();
    onVisualize.value(res);
    message.success("Packet sent");
  } catch (error) {
    getErrorResponse(error);
  } finally {
    sending.value = false;
  }
};

const resetFlow = () => {
  formState.ininf = null;
  formState.outinf = null;
  formState.saddr = null;
  formState.daddr = null;

  const iface = getCurIface();
  if (!iface) return;

  if (flowState.value === "in") {
    formState.ininf = iface.ifname;
    formState.daddr = iface.addr;
  }
  else if (flowState.value === "out") {
    formState.outinf = iface.ifname;
    formState.saddr = iface.addr;
  }
}

const resetMac = () => {
  formState.smac = null;
  formState.dmac = null;

  if (!btnState.mac) return;

  const iface = getCurIface();
  if (!iface) return;

  if (flowState.value === "in") formState.dmac = iface.mac;
  else if (flowState.value === "out") formState.smac = iface.mac;
}

const getCurIface = () => {
  return interfaces.value.find(
    (item) => item.ifname === ifaceState.value
  );
}

const onFlowChange = () => {
  resetFlow();
  resetMac();
};

const handleBtnClick = (item) => {
  btnState[item] = !btnState[item];
  switch (item) {
    case "flow":
      flowState.value = btnState[item] && "in";
      resetFlow();
      break;
    case "mac":
      resetMac();
      break;
    case "mark":
      formState.mark = null;
      break;
  }
};
</script>

<template>
  <div class="packet-form">
    <a-typography-title :level="3">Packet Simulator</a-typography-title>
    <a-space style="margin-bottom: 15px">
      <a-space-compact>
        <a-button :type="btnState.flow ? 'primary' : 'default'" @click="handleBtnClick('flow')">Flow</a-button>
        <a-button :type="btnState.mac ? 'primary' : 'default'" @click="handleBtnClick('mac')">Mac</a-button>
        <a-button :type="btnState.mark ? 'primary' : 'default'" @click="handleBtnClick('mark')">Mark</a-button>
      </a-space-compact>
    </a-space>
    <a-form layout="inline" :model="formState" @finish="onFinish">
      <a-form-item v-if="btnState.flow">
        <a-select style="width: 80px" placeholder="Flow" @change="onFlowChange" v-model:value="flowState"
          :options="flows" />
      </a-form-item>
      <a-form-item v-if="btnState.flow">
        <a-select style="width: 120px" placeholder="Ether" @change="onFlowChange" v-model:value="ifaceState"
          :options="ethers" />
      </a-form-item>
      <a-form-item>
        <a-select style="width: 120px" placeholder="State" v-model:value="formState.state" :options="states"></a-select>
      </a-form-item>
      <a-form-item>
        <a-select style="width: 120px" placeholder="Protocol" v-model:value="formState.prot" :options="prots"></a-select>
      </a-form-item>
      <a-form-item v-if="btnState.mac">
        <a-input v-model:value="formState.smac" placeholder="Source MAC" />
      </a-form-item>
      <a-form-item v-if="btnState.mac">
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
      <a-form-item v-if="btnState.mark">
        <a-input style="width: 120px" v-model:value="formState.mark" placeholder="Mark" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="sending">Send</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>
<style scoped>
.ant-form-item {
  margin-right: 10px;
  margin-top: 10px;
}
</style>
