import { ref } from "vue";
import { message } from "ant-design-vue";

export const useErrorHandling = () => {
  const errorValue = ref(null);
  const getErrorResponse = async (error, showMessageOnly = true) => {
    const data = await error?.response?.json();
    if (data) {
      if (showMessageOnly) message.error(data?.detail || "Error!");
      else errorValue.value = data?.detail || "Error!";
    } else {
      if (showMessageOnly) message.error("Error!");
      else errorValue.value = "Error!";
    }
  };
  return { getErrorResponse, errorValue };
};
