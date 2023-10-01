import { createRouter, createWebHistory } from "vue-router";
import IptablesPage from "@/views/IptablesPage.vue";
import PacketPage from "@/views/PacketPage.vue";
import NotFoundPage from "@/views/NotFoundPage.vue";

const routes = [
  {
    path: "/",
    name: "IptablesPage",
    component: IptablesPage,
  },
  {
    path: "/:netns",
    name: "PacketPage",
    component: PacketPage,
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFoundPage",
    component: NotFoundPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
